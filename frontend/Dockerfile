FROM public.ecr.aws/docker/library/node:20-slim

RUN mkdir /app
COPY package.json package-lock.json /app/
RUN cd /app && npm install

COPY . /app

EXPOSE 5173

CMD ["npm", "run", "dev", "--prefix", "/app", "--", "--host"]
