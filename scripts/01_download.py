# -*- coding: utf-8 -*-
"""
01_download.py — Baixa as fotos de um perfil público do Instagram com instaloader.

Por que cookies e não login por senha?
  O Instagram hoje bloqueia o acesso anônimo (403 Forbidden) e frequentemente joga
  o login por senha num "checkpoint" em loop. A forma que funcionou de forma estável
  foi reaproveitar a SESSÃO já logada no navegador, injetando os cookies no instaloader.

Como obter os cookies (uma vez):
  1. Faça login no instagram.com no navegador (ex.: Edge/Chrome).
  2. F12 -> aba Application/Aplicativo -> Cookies -> https://www.instagram.com
  3. Copie os valores de: sessionid, csrftoken, ds_user_id
  4. Exponha-os como variáveis de ambiente (NUNCA hardcode no arquivo):

     Windows (PowerShell):
       $env:IG_SESSIONID  = "..."
       $env:IG_CSRFTOKEN  = "..."
       $env:IG_DS_USER_ID = "..."

     Linux/Mac (bash):
       export IG_SESSIONID=...
       export IG_CSRFTOKEN=...
       export IG_DS_USER_ID=...

  Obs.: o sessionid é sensível (dá acesso à conta). Faça logout no Instagram para
  invalidá-lo quando terminar.

Uso:
  python 01_download.py <perfil> [pasta_destino]
  ex.: python 01_download.py neuroglobe ./posts
"""
import os
import sys
import time

import instaloader
from instaloader import Profile
from instaloader.exceptions import ConnectionException, QueryReturnedForbiddenException

TARGET = sys.argv[1] if len(sys.argv) > 1 else "neuroglobe"
DEST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "posts")

cookies = {
    "sessionid": os.environ.get("IG_SESSIONID", ""),
    "csrftoken": os.environ.get("IG_CSRFTOKEN", ""),
    "ds_user_id": os.environ.get("IG_DS_USER_ID", ""),
}
if not cookies["sessionid"]:
    sys.exit("ERRO: defina as variáveis de ambiente IG_SESSIONID / IG_CSRFTOKEN / IG_DS_USER_ID.")

L = instaloader.Instaloader(
    dirname_pattern=DEST,
    download_videos=False,           # só fotos
    download_video_thumbnails=False,
    download_comments=False,
    save_metadata=False,
    post_metadata_txt_pattern="",    # não gera .txt de legenda
    max_connection_attempts=5,       # resiliência a 403/503 passageiros
    request_timeout=60,
)

# injeta a sessão do navegador
for k, v in cookies.items():
    if v:
        L.context._session.cookies.set(k, v, domain=".instagram.com")

who = L.test_login()
print("Logado como:", who)
if not who:
    sys.exit("FALHOU: sessão inválida — refaça a captura dos cookies.")
L.context.username = who

profile = Profile.from_username(L.context, TARGET)
print(f"Perfil @{TARGET}: {profile.mediacount} publicações no total.")

# instaloader PULA arquivos que já existem -> o script é retomável:
# se cair no meio, é só rodar de novo que ele continua de onde parou.
n, falhas = 0, []
for post in profile.get_posts():
    tentativas = 0
    while True:
        try:
            L.download_post(post, target="posts")
            n += 1
            break
        except (ConnectionException, QueryReturnedForbiddenException) as e:
            tentativas += 1
            if tentativas >= 3:
                print(f"PULANDO {post.shortcode} após {tentativas} falhas: {e}")
                falhas.append(post.shortcode)
                break
            print(f"Erro em {post.shortcode} (tentativa {tentativas}), esperando 30s: {e}")
            time.sleep(30)
        except Exception as e:
            print(f"PULANDO {post.shortcode} (erro inesperado): {e}")
            falhas.append(post.shortcode)
            break

print(f"CONCLUÍDO. {n} publicações baixadas. {len(falhas)} puladas: {falhas}")
