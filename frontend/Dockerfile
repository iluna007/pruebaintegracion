# Usar una imagen base oficial de Node
FROM node:18-alpine

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Exponer el puerto de desarrollo de Vite
EXPOSE 5173

# Comando por defecto (ya no es necesario si lo defines en docker-compose, 
# pero puede ser útil tenerlo aquí)
CMD ["npm", "run", "dev"]
