import os
import re
import urllib.parse
import urllib.request
import logging
from typing import Optional, List

logger = logging.getLogger("news_briefing.whatsapp")


def markdown_to_whatsapp(markdown_text: str) -> str:
    """
    Converte formatação Markdown padrão para a sintaxe do WhatsApp:
    - **negrito** -> *negrito*
    - *itálico* -> _itálico*
    - # Título -> *TÍTULO*
    - [texto](link) -> texto (link)
    """
    text = markdown_text

    # Converte links [texto](url) -> texto (url)
    text = re.sub(r"\[(.*?)\]\((https?://.*?)\)", r"\1 (\2)", text)

    # Converte cabeçalhos # Título para *TÍTULO*
    text = re.sub(r"^#+\s+(.*?)$", r"\n*\1*\n", text, flags=re.MULTILINE)

    # Converte citações (> texto)
    text = re.sub(r"^>\s+(.*?)$", r"💬 _\1_", text, flags=re.MULTILINE)

    # Converte negrito Markdown (**texto**) para negrito WhatsApp (*texto*)
    text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)

    # Remove divisórias Markdown ---
    text = re.sub(r"---", r"════════════════", text)

    # Remove tags HTML residuais
    text = re.sub(r"<[^>]+>", "", text)

    # Remove espaços em branco excessivos
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text


def split_message(text: str, max_length: int = 3000) -> List[str]:
    """Divide mensagens muito longas em partes para respeitar o limite do WhatsApp."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    lines = text.split("\n")
    current_chunk = []
    current_length = 0

    for line in lines:
        line_len = len(line) + 1
        if current_length + line_len > max_length:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = line_len
        else:
            current_chunk.append(line)
            current_length += line_len

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


def send_whatsapp_message(
    message: str,
    phone: Optional[str] = None,
    apikey: Optional[str] = None,
    timeout: int = 20
) -> bool:
    """
    Envia mensagem via CallMeBot WhatsApp API (serviço gratuito para uso pessoal).
    
    Parâmetros:
    - phone: Número no formato internacional sem + e sem hífens (ex: 5541999999999)
    - apikey: Chave gratuita fornecida pelo bot do CallMeBot
    """
    target_phone = phone or os.getenv("WHATSAPP_PHONE")
    target_key = apikey or os.getenv("WHATSAPP_APIKEY")

    if not target_phone or not target_key:
        logger.warning(
            "Configurações de WhatsApp incompletas. "
            "Defina WHATSAPP_PHONE e WHATSAPP_APIKEY no arquivo .env."
        )
        return False

    # Limpa o telefone (apenas números)
    clean_phone = re.sub(r"\D", "", target_phone)

    # Converte o markdown para texto formatado do WhatsApp
    wa_text = markdown_to_whatsapp(message)
    chunks = split_message(wa_text, max_length=3000)

    success_all = True
    for i, chunk in enumerate(chunks, 1):
        if len(chunks) > 1:
            chunk = f"*(Parte {i}/{len(chunks)})*\n\n" + chunk

        encoded_text = urllib.parse.quote(chunk)
        url = (
            f"https://api.callmebot.com/whatsapp.php?"
            f"phone={clean_phone}&text={encoded_text}&apikey={target_key}"
        )

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "NewsBriefing/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                resp_text = response.read().decode("utf-8", errors="ignore")
                if "error" in resp_text.lower() or "fail" in resp_text.lower():
                    logger.error(f"Erro retornado pelo CallMeBot: {resp_text}")
                    success_all = False
                else:
                    logger.info(f"Mensagem do WhatsApp enviada com sucesso (parte {i}/{len(chunks)})")
        except Exception as e:
            logger.error(f"Falha na requisição para o CallMeBot: {e}")
            success_all = False

    return success_all
