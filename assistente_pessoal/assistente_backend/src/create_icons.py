#!/usr/bin/env python3
"""
Gerador de ícones para PWA do IAON Universal
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Criar ícone com tamanho específico"""
    # Criar imagem com fundo gradiente
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fundo com gradiente simulado (azul para roxo)
    for y in range(size):
        color_ratio = y / size
        r = int(102 + (118 - 102) * color_ratio)  # 667eea para 764ba2
        g = int(126 + (75 - 126) * color_ratio)
        b = int(234 + (162 - 234) * color_ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # Adicionar círculo de fundo
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=(255, 255, 255, 40))
    
    # Adicionar emoji do robô (simulado com texto)
    try:
        font_size = size // 3
        # Usar fonte padrão do sistema
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("segoeui.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Desenhar emoji de robô
        robot_text = "🤖"
        bbox = draw.textbbox((0, 0), robot_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), robot_text, fill=(255, 255, 255, 255), font=font)
        
    except Exception as e:
        # Fallback: desenhar círculo simples
        center = size // 2
        radius = size // 4
        draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                    fill=(255, 255, 255, 255))
    
    # Salvar
    img.save(filename, 'PNG')
    print(f"✅ Ícone criado: {filename} ({size}x{size})")

def main():
    """Criar todos os ícones necessários"""
    print("🎨 Criando ícones para PWA...")
    
    try:
        create_icon(192, 'icon-192.png')
        create_icon(512, 'icon-512.png')
        print("✅ Todos os ícones foram criados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar ícones: {e}")
        print("ℹ️ Usando ícones alternativos...")
        
        # Criar ícones simples sem PIL
        create_simple_icon(192, 'icon-192.png')
        create_simple_icon(512, 'icon-512.png')

def create_simple_icon(size, filename):
    """Criar ícone simples sem dependências"""
    # Criar arquivo SVG e converter
    svg_content = f'''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea"/>
                <stop offset="100%" style="stop-color:#764ba2"/>
            </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#grad)" rx="{size//8}"/>
        <circle cx="{size//2}" cy="{size//2}" r="{size//4}" fill="white" opacity="0.9"/>
        <text x="{size//2}" y="{size//2 + size//12}" text-anchor="middle" 
              font-size="{size//4}" fill="#333">AI</text>
    </svg>'''
    
    with open(f'{filename}.svg', 'w') as f:
        f.write(svg_content)
    
    print(f"✅ Ícone SVG criado: {filename}.svg")

if __name__ == "__main__":
    main()
