# pwa

## Docker Setup

### Development

    /frontend$ docker build -t rev-img:dev .
    /frontend$ docker run -v ${PWD}/pwa:/pwa -v /pwa/node_modules -p 8081:8080 --rm rev-img:dev

### Production

    /frontend$ docker build -f Dockerfile.prod -t rev-img:prod .
    /frontend$ docker run -d -p 8081:80 rev-img:prod

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
