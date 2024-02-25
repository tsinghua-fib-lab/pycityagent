FROM registry.fiblab.net/general/dev:latest as builder

WORKDIR /build
COPY . /build
ENV PIP_NO_CACHE_DIR=1
RUN pip3 install --upgrade pip \ 
    && pip3 install pdoc \
    && ./scripts/init.sh \
    && ./scripts/install-local.sh \
    && ./scripts/gen_docs.sh

FROM node:18-alpine
ENV NODE_ENV=production
WORKDIR /home/node/app

# Install serve
RUN yarn global add serve

# Copy build files
COPY --from=builder /build/docs ./build

EXPOSE 80

CMD serve build -p 80
