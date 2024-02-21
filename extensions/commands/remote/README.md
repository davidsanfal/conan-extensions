## Run conan remotely

**Dependencies**

```shellSession
$ pip install docker
```

**Run a conan create inside Docker [MacOS Only]**

**1.** Create the `conandocker` profile.

```
[settings]
arch=x86_64
build_type=Release
compiler=gcc
compiler.cppstd=gnu17
compiler.libcxx=libstdc++11
compiler.version=11
os=Linux
```

**2.** Compile zlib/1.3.1 for linux inside a Docker image.


```shellSession
$ git clone git@github.com:conan-io/conan-center-index.git
$ conan remote:create docker ${PWD}/conan-center-index/recipes/zlib/all --name=zlib --version=1.3.1 --build='*' --profile:build=conandocker --profile:host=conandocker
```
