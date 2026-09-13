import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from .deduplicator import ClusteredStory

logger = logging.getLogger("news_briefing.synthesizer")


def build_editorial_prompt(stories: List[ClusteredStory], language: str = "pt-BR") -> str:
    """Monta o prompt para o Gemini com as notícias estruturadas da manhã."""
    stories_data = []
    for idx, story in enumerate(stories[:40], 1):  # Limita aos 40 eventos principais
        sources_str = ", ".join(story.sources)
        links_preview = [f"{l['source']}: {l['url']}" for l in story.links[:2]]
        stories_data.append({
            "id": idx,
            "titulo": story.primary_title,
            "categoria": story.category,
            "veiculos": sources_str,
            "qtd_fontes": len(story.sources),
            "resumos": story.items[0].summary if story.items else "",
            "links": links_preview
        })

    json_payload = json.dumps(stories_data, ensure_ascii=False, indent=2)

    prompt = f"""Você é o Editor-Chefe de Inteligência de Notícias matinal.
Sua missão é ler a lista de fatos e notícias coletados nesta manhã a partir de grandes agências e veículos (Reuters, CNN, UOL, G1, BBC, InfoMoney, etc.) e produzir um **Briefing Matinal Executivo, Único e Sucinto**.

Data do Briefing: {datetime.now().strftime('%d/%m/%Y')}
Idioma de saída: Português (Brasil)

### Diretrizes de Escrita:
1. **Sucinto e Direto ao Ponto**: Sem enrolação. Use bullet points claros, negrito para destaques e explique 'por que importa'.
2. **Visão Sintetizada**: Se vários veículos noticiaram o mesmo fato (ex: Reuters e CNN), unifique em uma única análise rica, mencionando as fontes.
3. **Imparcialidade e Rigor**: Destaque fatos confirmados.

### Estrutura Obrigatória do Relatório:

# 🌅 Briefing Matinal de Notícias — {datetime.now().strftime('%d/%m/%Y')}

> **Tempo estimado de leitura:** 3 minutos  
> **Fontes analisadas:** Reuters, CNN, UOL, G1, BBC, InfoMoney

---

## ⚡ Destaques da Manhã (Top 3 Acontecimentos)
*Os fatos mais críticos que você precisa saber antes do dia começar.*
- **[Título do Fato 1]**: Síntese explicativa em 2 ou 3 frases. *Por que importa:* Impacto direto. *(Fontes: Nome das Fontes)*
- ...

---

## 🇧🇷 Brasil & Política
*Os principais desdobramentos em Brasília, estados e sociedade.*
- ...

---

## 📈 Economia, Mercados & Negócios
*Dólar, juros, bolsas globais, inflação e cenário corporativo.*
- ...

---

## 🌍 Cenário Internacional & Geopolítica
*Crises, acordos internacionais e eleições pelo mundo via Reuters, CNN e BBC.*
- ...

---

## 💡 Tecnologia & Inovação
*Inteligência artificial, segurança digital e grandes empresas tech.*
- ...

---

## 🎯 Radar Rápido
*Pílulas de notícias em 1 frase para ficar por dentro de tudo.*
- ...

---

### Dados brutos coletados das notícias:
```json
{json_payload}
```

Escreva agora o briefing completo em Markdown com formatação profissional, elegante e links quando pertinente.
"""
    return prompt


def generate_briefing_with_gemini(
    stories: List[ClusteredStory],
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash",
    language: str = "pt-BR"
) -> str:
    """Gera o relatório executivo matinal usando a API do Google Gemini."""
    if not stories:
        return "# 🌅 Briefing Matinal de Notícias\n\nNenhuma notícia recente encontrada para a janela de tempo selecionada."

    effective_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not effective_key:
        logger.warning("GEMINI_API_KEY não encontrada. Gerando relatório em modo fallback.")
        return generate_fallback_report(stories)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=effective_key)
        prompt = build_editorial_prompt(stories, language=language)

        config = types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=4000,
        )

        # Lista de modelos candidatos resilientes
        candidate_models = [model_name]
        for fallback_m in ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.7-flash"]:
            if fallback_m not in candidate_models:
                candidate_models.append(fallback_m)

        last_error = None
        for current_model in candidate_models:
            try:
                logger.info(f"Tentando gerar síntese com o modelo: {current_model}")
                response = client.models.generate_content(
                    model=current_model,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_error = e
                err_str = str(e)
                # Se for 404 (modelo descontinuado) ou 503 (alta demanda temporária), tenta o próximo candidato
                if any(code in err_str for code in ["404", "503", "NOT_FOUND", "UNAVAILABLE", "high demand"]):
                    logger.warning(f"Modelo {current_model} indisponível temporariamente ({err_str[:80]}...). Tentando próximo modelo...")
                    continue
                else:
                    raise e

        logger.error(f"Nenhum modelo respondeu com sucesso: {last_error}")
        return generate_fallback_report(stories, error_msg=str(last_error))

    except Exception as e:
        logger.error(f"Erro ao chamar a API Gemini: {e}")
        return generate_fallback_report(stories, error_msg=str(e))


def generate_fallback_report(stories: List[ClusteredStory], error_msg: Optional[str] = None) -> str:
    """Gera um relatório estruturado localmente quando o Gemini não está acessível."""
    now_str = datetime.now().strftime("%d/%m/%Y às %H:%M")
    lines = [
        f"# 🌅 Briefing Matinal de Notícias (Modo Estruturado)",
        f"> **Gerado em:** {now_str} | **Total de matérias agrupadas:** {len(stories)}",
        ""
    ]

    if error_msg:
        lines.append(f"> ⚠️ **Aviso de IA:** A síntese com Gemini não pôde ser executada ({error_msg}). Exibindo agregação estruturada direta das fontes.")
    else:
        lines.append("> 💡 **Dica:** Configure `GEMINI_API_KEY` no arquivo `.env` para ativar a síntese com IA executiva.")

    lines.append("\n---\n")

    # Agrupar por categoria
    by_category: Dict[str, List[ClusteredStory]] = {}
    for st in stories:
        cat = st.category or "Geral"
        by_category.setdefault(cat, []).append(st)

    lines.append("## ⚡ Principais Manchetes da Manhã\n")
    for st in stories[:5]:
        sources_str = ", ".join(st.sources)
        first_link = st.links[0]["url"] if st.links else "#"
        lines.append(f"- **[{st.primary_title}]({first_link})**")
        lines.append(f"  *Fontes:* {sources_str}")
        if st.items and st.items[0].summary:
            lines.append(f"  {st.items[0].summary[:180]}...")
        lines.append("")

    lines.append("---\n")

    cat_icons = {
        "Brasil": "🇧🇷",
        "Internacional": "🌍",
        "Economia": "📈",
        "Tecnologia": "💡",
        "Geral": "📰"
    }

    for cat, cat_stories in by_category.items():
        icon = cat_icons.get(cat, "📌")
        lines.append(f"## {icon} {cat}\n")
        for st in cat_stories[:6]:
            sources_str = ", ".join(st.sources)
            first_link = st.links[0]["url"] if st.links else "#"
            lines.append(f"- [{st.primary_title}]({first_link}) *({sources_str})*")
        lines.append("")

    return "\n".join(lines)


def build_regional_editorial_prompt(stories: List[ClusteredStory], language: str = "pt-BR") -> str:
    """Monta o prompt para o Gemini focado nas notícias de Curitiba, RMC e Paraná."""
    # Filtra ruídos astrológicos/loterias comuns em portais regionais
    filtered_stories = []
    ignored_keywords = ["horóscopo", "horoscopo", "signos", "tarot", "lotofácil", "megasena", "mega-sena", "quina"]
    for s in stories:
        title_lower = s.primary_title.lower()
        if any(k in title_lower for k in ignored_keywords):
            continue
        filtered_stories.append(s)

    stories_data = []
    for idx, story in enumerate(filtered_stories[:50], 1):
        sources_str = ", ".join(story.sources)
        links_preview = [f"{l['source']}: {l['url']}" for l in story.links[:2]]
        stories_data.append({
            "id": idx,
            "titulo": story.primary_title,
            "categoria": story.category,
            "veiculos": sources_str,
            "qtd_fontes": len(story.sources),
            "resumos": story.items[0].summary if story.items else "",
            "links": links_preview
        })

    json_payload = json.dumps(stories_data, ensure_ascii=False, indent=2)

    prompt = f"""Você é o Editor-Chefe de Notícias de Curitiba e do Paraná.
Sua missão é analisar as notícias do dia anterior e do início desta manhã publicadas pelos principais veículos paranaenses (**Tribuna do Paraná, Bem Paraná e Banda B**) e produzir o informativo matinal **"Fatos da Região"**.

Data do Briefing: {datetime.now().strftime('%d/%m/%Y')}
Edição: 09:00 (Fatos do dia anterior e início da manhã)
Idioma de saída: Português (Brasil)

### Diretrizes Editoriais:
1. **Foco Estritamente Regional**: Curitiba, Região Metropolitana (São José dos Pinhais, Colombo, Araucária, Fazenda Rio Grande, Pinhais, etc.), Litoral e Interior do Paraná.
2. **Elimine Frivolidades**: Ignore completamente horóscopo, previsões de signos, tarot, fofocas ou sorteios de loteria. Foque em jornalismo factual, prestação de serviços, segurança, trânsito e decisões públicas.
3. **Visão Sintetizada**: Quando múltiplos veículos noticiarem o mesmo fato (ex: acidente coberto por Banda B e Tribuna), una as informações em um único parágrafo completo e cite as fontes.
4. **Impacto Prático ('Por que importa')**: Destaque como o fato afeta a vida, o deslocamento ou o bolso do cidadão paranaense.

### Estrutura Obrigatória do Relatório:

# 🏙️ Fatos da Região — Curitiba & Paraná ({datetime.now().strftime('%d/%m/%Y')})

> **Edição Matinal das 09h** | Cobertura das últimas 24 horas (dia anterior + início da manhã)  
> **Fontes:** Tribuna do Paraná • Bem Paraná • Banda B  

---

## ⚡ Destaques da Região (Top 3 Acontecimentos)
*Os fatos mais importantes do dia em Curitiba e no Paraná.*
- **[Título do Fato 1]**: Síntese detalhada em 2 ou 3 frases. *Impacto direto:* Como isso mexe com a rotina ou a região. *(Fontes: Veículos)*
- ...

---

## 🚨 Segurança Pública & Ocorrências
*Operações policiais, acidentes, investigações e alertas da Defesa Civil no estado.*
- ...

---

## 🚗 Trânsito, Mobilidade & Cidade
*Rodovias (BR-277, BR-376, Contornos), linhas de ônibus, obras, abastecimento e tempo em Curitiba e RMC.*
- ...

---

## ⚖️ Política Paranaense & Gestão Pública
*Prefeitura de Curitiba, Governo do Estado (Palácio Iguaçu), Assembleia Legislativa (Alep) e Câmaras Municipais.*
- ...

---

## 💼 Economia Local & Negócios
*Empregos, comércio, agronegócio paranaense e investimentos na região.*
- ...

---

## 🎭 Cidade, Comunidade & Lazer
*Parques, eventos culturais, gastronomia e acontecimentos da vida urbana curitibana.*
- ...

---

## 🎯 Giro RMC & Interior
*Pílulas rápidas em 1 linha sobre municípios da região metropolitana e cidades do interior/litoral.*
- ...

---

### Dados brutos coletados dos portais regionais:
```json
{json_payload}
```

Escreva agora o informativo completo em Markdown profissional, direto, claro e bem diagramado.
"""
    return prompt


def generate_regional_briefing_with_gemini(
    stories: List[ClusteredStory],
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash",
    language: str = "pt-BR"
) -> str:
    """Gera a síntese editorial do Fatos da Região com Gemini."""
    if not stories:
        return "# 🏙️ Fatos da Região — Curitiba & Paraná\n\nNenhuma notícia regional encontrada para o período selecionado."

    effective_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not effective_key:
        logger.warning("GEMINI_API_KEY não encontrada. Gerando Fatos da Região em modo fallback.")
        return generate_fallback_regional_report(stories)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=effective_key)
        prompt = build_regional_editorial_prompt(stories, language=language)

        config = types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=4000,
        )

        candidate_models = [model_name]
        for fallback_m in ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.7-flash"]:
            if fallback_m not in candidate_models:
                candidate_models.append(fallback_m)

        last_error = None
        for current_model in candidate_models:
            try:
                logger.info(f"Tentando gerar Fatos da Região com o modelo: {current_model}")
                response = client.models.generate_content(
                    model=current_model,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_error = e
                err_str = str(e)
                if any(code in err_str for code in ["404", "503", "NOT_FOUND", "UNAVAILABLE", "high demand"]):
                    logger.warning(f"Modelo {current_model} indisponível temporariamente ({err_str[:80]}...). Tentando próximo...")
                    continue
                else:
                    raise e

        logger.error(f"Nenhum modelo respondeu com sucesso: {last_error}")
        return generate_fallback_regional_report(stories, error_msg=str(last_error))

    except Exception as e:
        logger.error(f"Erro ao chamar a API Gemini para Fatos da Região: {e}")
        return generate_fallback_regional_report(stories, error_msg=str(e))


def generate_fallback_regional_report(stories: List[ClusteredStory], error_msg: Optional[str] = None) -> str:
    """Gera um relatório estruturado localmente para Fatos da Região quando Gemini não está ativo."""
    now_str = datetime.now().strftime("%d/%m/%Y às %H:%M")
    lines = [
        f"# 🏙️ Fatos da Região — Curitiba & Paraná (Modo Estruturado)",
        f"> **Gerado em:** {now_str} | **Fontes:** Tribuna do Paraná • Bem Paraná • Banda B",
        f"> **Total de histórias agrupadas:** {len(stories)}",
        ""
    ]

    if error_msg:
        lines.append(f"> ⚠️ **Aviso de IA:** A síntese com Gemini não pôde ser executada ({error_msg}). Exibindo agregação direta das fontes.")
    else:
        lines.append("> 💡 **Dica:** Configure `GEMINI_API_KEY` no `.env` para ativar a síntese com IA executiva.")

    lines.append("\n---\n")

    # Filtra ruídos astrológicos/loterias comuns
    ignored_keywords = ["horóscopo", "horoscopo", "signos", "tarot", "lotofácil", "megasena", "mega-sena", "quina"]
    valid_stories = [
        st for st in stories
        if not any(k in st.primary_title.lower() for k in ignored_keywords)
    ]

    lines.append("## ⚡ Principais Notícias de Curitiba e Paraná\n")
    for st in valid_stories[:10]:
        sources_str = ", ".join(st.sources)
        first_link = st.links[0]["url"] if st.links else "#"
        lines.append(f"- **[{st.primary_title}]({first_link})**")
        lines.append(f"  *Fontes:* {sources_str}")
        if st.items and st.items[0].summary:
            lines.append(f"  {st.items[0].summary[:180]}...")
        lines.append("")

    return "\n".join(lines)

