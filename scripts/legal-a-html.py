"""Genera web/privacidad/index.html y web/condiciones/index.html desde docs/legal/*.md.
Uso (desde la raíz del repositorio): python3 web/scripts/legal-a-html.py
Los .md salen de mobile/i18n/legal.es.json con `npm run legal`; esta es la copia para la web."""
import html, re, pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[2]

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    t = re.sub(r'([\w.+-]+@[\w-]+\.[\w.]+)', r'<a href="mailto:\1">\1</a>', t)
    return t

def md(texto):
    out, lista, tabla = [], False, []
    def cerrar():
        nonlocal lista, tabla
        if lista: out.append('</ul>'); lista = False
        if tabla:
            cab, *filas = tabla
            out.append('<div class="tabla"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cab) + '</tr></thead><tbody>'
                       + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in f) + '</tr>' for f in filas) + '</tbody></table></div>')
            tabla = []
    for l in texto.splitlines():
        if l.startswith('|'):
            celdas = [c.strip() for c in l.strip('|').split('|')]
            if not all(re.fullmatch(r'-+', c) for c in celdas): tabla.append(celdas)
            continue
        if l.startswith('- '):
            if tabla: cerrar()
            if not lista: out.append('<ul>'); lista = True
            out.append(f'<li>{inline(l[2:])}</li>'); continue
        cerrar()
        if not l.strip(): continue
        m = re.match(r'(#{1,3}) (.*)', l)
        if m: n = len(m.group(1)); out.append(f'<h{n}>{inline(m.group(2))}</h{n}>')
        else: out.append(f'<p>{inline(l)}</p>')
    cerrar()
    return '\n'.join(out)

PLANTILLA = '''<!doctype html>
<html lang="es-ES">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} · Keinext</title>
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://keinext.com/{ruta}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
/* Open Sans servida desde keinext.com (sin Google Fonts: las visitas no mandan su IP a Google) */
@font-face{{font-family:"Open Sans";font-style:normal;font-weight:400;font-display:swap;src:url(/assets/fuentes/OpenSans_400Regular.ttf) format("truetype")}}
@font-face{{font-family:"Open Sans";font-style:italic;font-weight:400;font-display:swap;src:url(/assets/fuentes/OpenSans_400Regular_Italic.ttf) format("truetype")}}
@font-face{{font-family:"Open Sans";font-style:normal;font-weight:600;font-display:swap;src:url(/assets/fuentes/OpenSans_600SemiBold.ttf) format("truetype")}}
@font-face{{font-family:"Open Sans";font-style:normal;font-weight:700;font-display:swap;src:url(/assets/fuentes/OpenSans_700Bold.ttf) format("truetype")}}
@font-face{{font-family:"Open Sans";font-style:normal;font-weight:800;font-display:swap;src:url(/assets/fuentes/OpenSans_800ExtraBold.ttf) format("truetype")}}
:root{{--brand-dark:#9a513b;--sand:#f9f6f4;--text:#2b2421;--text-2:#605348;--line:#e5e3dc;--white:#fff}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Open Sans",system-ui,sans-serif;color:var(--text);background:var(--sand);line-height:1.6}}
.wrap{{max-width:46rem;margin:0 auto;padding:32px max(16px,env(safe-area-inset-left,0px)) 96px}}
a{{color:var(--brand-dark)}}
.volver{{display:inline-flex;align-items:center;min-height:44px;font-weight:700;text-decoration:none}}
h1{{font-size:clamp(2rem,7vw,3rem);line-height:1.05;font-weight:800;letter-spacing:-.02em;margin:24px 0 8px}}
h2{{font-size:1.5rem;margin:40px 0 8px}} h3{{font-size:1.125rem;margin:28px 0 4px}}
p,li{{color:var(--text-2)}} li{{margin:4px 0}}
.tabla{{overflow-x:auto;margin:16px 0}} table{{border-collapse:collapse;width:100%;background:var(--white);font-size:.9375rem}}
th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
:focus-visible{{outline:3px solid #d4722a;outline-offset:3px}}
</style>
</head>
<body>
<main class="wrap">
<a class="volver" href="/">← Volver a Keinext</a>
{cuerpo}
</main>
</body>
</html>
'''

for md_nombre, ruta in [('politica-de-privacidad.md', 'privacidad'), ('condiciones-de-uso.md', 'condiciones')]:
    texto = (RAIZ / 'docs/legal' / md_nombre).read_text(encoding='utf-8')
    # quitar la nota interna de generación («Generado desde…: no se edita aquí.»)
    texto = re.sub(r' Generado desde [^_]*?no se edita aquí\.', '', texto)
    titulo = re.search(r'^# (.*)', texto, re.M).group(1)
    destino = RAIZ / 'web' / ruta / 'index.html'
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(PLANTILLA.format(titulo=titulo, ruta=ruta, cuerpo=md(texto)), encoding='utf-8')
    print(destino.relative_to(RAIZ))
