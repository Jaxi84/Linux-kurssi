
#!/bin/bash
# server-setup.sh - Aja tämä kerran uudella serverillä (Ubuntu 24.04+)

set -euo pipefail

echo "📦 Päivitetään paketit..."
sudo apt update && sudo apt upgrade -y

echo "🔧 Asennetaan LEMP-stack (Ubuntu:n oletus-PHP 8.3)..."
sudo apt install -y nginx mysql-server php-fpm php-mysql php-cli \
  php-curl php-xml php-mbstring php-zip git curl unzip

# Valinnainen: Composer (PHP-riippuvuuksille)
if ! command -v composer >/dev/null 2>&1; then
  echo "📦 Asennetaan Composer..."
  EXPECTED_CHECKSUM="$(curl -s https://getcomposer.org/installer.sig)"
  php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
  ACTUAL_CHECKSUM="$(php -r "echo hash_file('sha384', 'composer-setup.php');")"
  if [ "$EXPECTED_CHECKSUM" != "$ACTUAL_CHECKSUM" ]; then
      >&2 echo 'ERROR: Invalid composer installer checksum'
      rm composer-setup.php
      exit 1
  fi
  sudo php composer-setup.php --install-dir=/usr/local/bin --filename=composer
  rm composer-setup.php
fi

# Valinnainen: Node.js LTS (jos käytät npm buildia)
if ! command -v node >/dev/null 2>&1; then
  echo "📦 Asennetaan Node.js (LTS via Nodesource)..."
  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
  sudo apt install -y nodejs
fi

echo "🔐 Luodaan deployment-käyttäjä..."
if ! id deployer >/dev/null 2>&1; then
  sudo useradd -m -s /bin/bash deployer
fi
sudo usermod -aG www-data deployer

echo "📁 Luodaan sovellushakemisto..."
sudo mkdir -p /var/www/myapp
sudo chown deployer:www-data /var/www/myapp
sudo chmod 755 /var/www/myapp

echo "🔑 Konfiguroidaan SSH deployer-käyttäjälle..."
sudo -u deployer mkdir -p /home/deployer/.ssh
sudo -u deployer chmod 700 /home/deployer/.ssh
# Lisää deploy key: sudo -u deployer nano /home/deployer/.ssh/authorized_keys

echo "🗄️ Konfiguroidaan MySQL..."
# HUOM: vaihda salasana!
DB_NAME="myapp_db"
DB_USER="myapp"
DB_PASS="strong_password"
sudo mysql <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\`;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "🌐 Konfiguroidaan Nginx..."
# Selvitetään FPM-socket (Ubuntu 24.04: php8.3-fpm)
FPM_SOCK=$(sudo find /run/php -maxdepth 1 -type s -name "php*-fpm.sock" | head -n1)
if [ -z "$FPM_SOCK" ]; then
  # fallback
  FPM_SOCK="/run/php/php-fpm.sock"
fi

sudo tee /etc/nginx/sites-available/myapp >/dev/null <<EOF
server {
    listen 80;
    server_name example.com;
    root /var/www/myapp/public;
    index index.php index.html;

    access_log /var/log/nginx/myapp-access.log;
    error_log /var/log/nginx/myapp-error.log;

    location / {
        try_files \$uri \$uri/ /index.php?\$query_string;
    }

    location ~ \.php\$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:${FPM_SOCK};
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo "✅ Server setup complete!"
echo "📝 Muista:"
echo "  1. Lisää SSH-avain: /home/deployer/.ssh/authorized_keys"
echo "  2. Vaihda MySQL salasana: '${DB_PASS}'"
echo "  3. Aseta domain: server_name example.com;"
echo "  4. Ota SSL käyttöön (kun DNS osoittaa tähän): sudo snap install --classic certbot && sudo certbot --nginx -d example.com
