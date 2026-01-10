FROM node:18-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем package.json бэкенда
COPY backend/package*.json ./backend/

# Устанавливаем Node.js зависимости
WORKDIR /app/backend
RUN npm install

# === СКАЧИВАЕМ МОДЕЛЬ MOBILENET_V2 ЧЕРЕЗ GIT LFS ===
RUN mkdir -p /tmp/nsfwjs-repo
WORKDIR /tmp/nsfwjs-repo

# Инициализация репозитория и настройка sparse checkout (только нужная папка)
RUN git init && \
    git remote add origin https://github.com/infinitered/nsfwjs.git && \
    git config core.sparsecheckout true && \
    echo "models/mobilenet_v2/*" > .git/info/sparse-checkout && \
    git pull origin master

# Устанавливаем LFS и получаем бинарные файлы
RUN git lfs install && \
    git lfs fetch && \
    git lfs checkout

# Копируем файлы модели в папку backend
RUN mkdir -p /app/backend/nsfwjs/model && \
    cp models/mobilenet_v2/* /app/backend/nsfwjs/model/

# Возвращаемся в backend и копируем остальной код
WORKDIR /app/backend
COPY . /app/

# Создаём runtime-папки
RUN mkdir -p public temp

EXPOSE 3000

CMD ["npm", "start"]