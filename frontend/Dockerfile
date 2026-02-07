FROM public.ecr.aws/docker/library/node:20-slim

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
