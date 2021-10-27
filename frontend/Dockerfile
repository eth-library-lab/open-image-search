# single stage build with hot reloading
# base image
FROM node:14.15.4-slim

# set working directory
WORKDIR /pwa

# add `/app/node_modules/.bin` to $PATH
ENV PATH /pwa/node_modules/.bin:$PATH

# install and cache app dependencies
COPY pwa/package.json /pwa/package.json
RUN npm install
RUN npm install @vue/cli@4.5.6 -g

# start app
CMD ["npm", "run", "serve"]
