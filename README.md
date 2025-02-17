# MCRMasters-BE
Backend API server for MCRMasters

# How To Install
## git clone
```bash
git clone https://github.com/MCRMasters/MCRMasters-BE.git
```

## pyenv 설치
### 의존성 패키지 설치
```bash
sudo apt-get update
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl
```

### pyenv 설치스크립트 실행
```bash
curl https://pyenv.run | bash
```

### shell 설정 파일에 환경변수 추가 (~/.zshrc나 ~/.bashrc)
```
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

### 설정 적용
```bash
source ~/.bashrc  # bash 사용시
# 또는
source ~/.zshrc   # zsh 사용시
```

### pyenv 설치 확인
```bash
pyenv --version
```


### python 3.12.8 설치
```bash
pyenv install 3.12.8
```

## poetry 설치
### poetry 설치 파일 실행
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### shell 설정 파일에 환경변수 추가 (~/.zshrc나 ~/.bashrc)

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 설정 적용
```bash
source ~/.bashrc  # bash 사용시
# 또는
source ~/.zshrc   # zsh 사용시
```

### poetry 설치 확인
```bash
poetry --version
```

### poetry install
```bash
poetry install
```

## pre-commit
```bash
pre-commit install
```

## test
```bash
poetry run pytest
```