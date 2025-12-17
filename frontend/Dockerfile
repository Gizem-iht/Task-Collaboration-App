FROM node:18-alpine

WORKDIR /app

# Paket dosyaları
COPY package*.json ./

# Bağımlılıkları yükle
RUN npm install

# Tüm proje dosyaları
COPY . .

EXPOSE 8080

# Vue dev server
CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0"]
