FROM registry.fiblab.net/general/dev:latest as builder

WORKDIR /build
COPY . /build
ENV PIP_NO_CACHE_DIR=1

# Ensure the script has executable permission
RUN chmod +x ./scripts/gen_docs.sh \
    && pip3 install --upgrade pip --root-user-action=ignore \
    && pip3 install pdoc --root-user-action=ignore \
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