# Shared Apache Traffic Server 10.2.0 lab image (pin tag 10.2.0).
# Identical across sibling labs. OpenSSL, not boringssl+quiche.
FROM ubuntu:24.04 AS build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    g++ \
    cmake \
    ninja-build \
    pkg-config \
    python3 \
    libssl-dev \
    libpcre3-dev \
    libpcre2-dev \
    libhwloc-dev \
    libcap-dev \
    zlib1g-dev \
    libxml2-dev \
    libluajit-5.1-dev \
    libmagick++-dev \
    libbrotli-dev \
    libzstd-dev \
    libjemalloc-dev \
    libfmt-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . /src

RUN cmake -S /src -B /build -G Ninja \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/opt/ats \
      -DBUILD_TESTING=OFF \
      -DBUILD_REGRESSION_TESTING=OFF \
      -DENABLE_AUTEST=OFF \
      -DBUILD_EXPERIMENTAL_PLUGINS=ON \
      -DENABLE_CRIPTS=ON \
      -DLUAJIT=ON \
      -DENABLE_LUAJIT=ON \
      -DENABLE_QUICHE=OFF \
      -DENABLE_EXAMPLE=OFF \
 && cmake --build /build \
 && cmake --install /build \
 && /opt/ats/bin/traffic_server --version \
 && test -f /opt/ats/libexec/trafficserver/authproxy.so

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/ats/bin:${PATH}"

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    libpcre3 \
    libpcre2-8-0 \
    hwloc \
    libcap2 \
    libxml2 \
    luajit \
    libluajit-5.1-2 \
    libmagick++-6.q16-9t64 \
    libjemalloc2 \
    libfmt9 \
    libbrotli1 \
    libzstd1 \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/ats /opt/ats

RUN mkdir -p /opt/ats/var/trafficserver /opt/ats/var/log/trafficserver \
 && chown -R nobody:nogroup /opt/ats/var

EXPOSE 8080
CMD ["traffic_server"]
