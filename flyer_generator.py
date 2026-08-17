import io
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


DEFAULT_FONT = ImageFont.load_default()


def _get_system_font(size):
    candidates = [
        'C:/Windows/Fonts/arialbd.ttf',
        'C:/Windows/Fonts/arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/System/Library/Fonts/Arial.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return DEFAULT_FONT


class FlyerGenerator:
    def __init__(self, graphic_skill: dict):
        self.graphic_skill = graphic_skill
        self.config = graphic_skill.get('config', {})
        self.template_path = graphic_skill.get('template')

    def _get_font(self, size: int):
        font_path = self.config.get('font_path')
        if font_path and Path(font_path).exists():
            return ImageFont.truetype(font_path, size)
        return _get_system_font(size)

    def _load_variable_font(self, font_path: str, size: int, variation):
        """Load a font file and, if it's a variable-weight font and a named
        instance was requested (e.g. 'Bold'), select that instance. Google's
        current font distribution ships most families as a single variable
        file rather than per-weight statics -- see layout_engine.py's
        typography resolution. Static fonts (variation=None) just load
        directly. If the named instance doesn't exist on this particular
        font (declares different axis names), fall back to the font's
        default weight rather than raising -- a wrong weight is a cosmetic
        miss, not worth breaking flyer generation over."""
        font = ImageFont.truetype(font_path, size)
        if variation:
            try:
                font.set_variation_by_name(variation)
            except Exception:
                pass
        return font

    def _get_typography_font(self, layout: dict, role: str, size: int):
        """role is 'headline' or 'accent', matching the keys layout_engine.py
        resolves under layout['typography']. Falls back to the existing
        config/system font path whenever there's no typography block, no
        font file specified for that role, or the file doesn't resolve on
        disk -- typography-led skills (skill-quotes and similar) get their
        real font; every other skill is completely unaffected and keeps
        using _get_font() exactly as before."""
        typography = layout.get('typography')
        if not typography:
            return self._get_font(size)
        font_path = typography.get(f'{role}_font')
        if not font_path or not Path(font_path).exists():
            return self._get_font(size)
        try:
            return self._load_variable_font(font_path, size, typography.get(f'{role}_variation'))
        except Exception:
            return self._get_font(size)

    def _wrap_text(self, draw, text: str, font, max_width: int):
        words = text.split()
        lines = []
        line = ''
        for word in words:
            test = f'{line} {word}'.strip()
            try:
                bbox = draw.textbbox((0, 0), test, font=font)
                test_width = bbox[2] - bbox[0]
            except Exception:
                try:
                    test_width = font.getsize(test)[0]
                except Exception:
                    test_width = len(test) * (getattr(font, 'size', 12) // 2)
            if test_width <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def _apply_background(self, canvas: Image.Image) -> Image.Image:
        if self.template_path and Path(self.template_path).exists():
            return Image.open(self.template_path).convert('RGBA')
        width, height = canvas.size
        bg_color = self.config.get('background_color', '#ffffff')
        gradient = self.config.get('background_gradient')
        if gradient and isinstance(gradient, list) and len(gradient) == 2:
            top_color, bottom_color = gradient
            for y in range(height):
                blend = y / (height - 1) if height > 1 else 0
                r = int(int(top_color[1:3], 16) * (1 - blend) + int(bottom_color[1:3], 16) * blend)
                g = int(int(top_color[3:5], 16) * (1 - blend) + int(bottom_color[3:5], 16) * blend)
                b = int(int(top_color[5:7], 16) * (1 - blend) + int(bottom_color[5:7], 16) * blend)
                ImageDraw.Draw(canvas).line([(0, y), (width, y)], fill=(r, g, b))
            return canvas
        return Image.new('RGBA', (width, height), bg_color)

    def _add_photo_shadow(self, img: Image.Image, offset=(8, 8), blur=15, color=(0, 0, 0, 80)) -> Image.Image:
        shadow = Image.new('RGBA', (img.width + 40, img.height + 40), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle([20 + offset[0], 20 + offset[1], 20 + img.width + offset[0], 20 + img.height + offset[1]], 
                              fill=color)
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
        shadow.paste(img, (20, 20), img if img.mode == 'RGBA' else None)
        return shadow

    def _round_corners(self, img: Image.Image, radius: int) -> Image.Image:
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, img.width, img.height], radius=radius, fill=255)
        output = Image.new('RGBA', img.size, (0, 0, 0, 0))
        output.paste(img, (0, 0), mask)
        return output

    def _add_vignette(self, canvas: Image.Image, intensity=0.25) -> Image.Image:
        width, height = canvas.size
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        cx, cy = width // 2, height // 2
        max_dist = math.sqrt(cx**2 + cy**2)
        for y in range(0, height, 4):
            for x in range(0, width, 4):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                alpha = int(180 * intensity * (dist / max_dist) ** 2)
                if alpha > 5:
                    draw.rectangle([x, y, x+4, y+4], fill=(0, 0, 0, min(alpha, 120)))
        return Image.alpha_composite(canvas, overlay)

    def _add_watermark(self, canvas: Image.Image, text: str = "AUGEO PREVIEW") -> Image.Image:
        overlay = Image.new('RGBA', canvas.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        font = self._get_font(64)
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            tw, th = len(text) * 32, 64
        txt_img = Image.new('RGBA', (tw + 40, th + 40), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((20, 20), text, font=font, fill=(255, 255, 255, 70))
        rotated = txt_img.rotate(45, expand=True)
        rot_w, rot_h = rotated.size
        for y in range(-rot_h, canvas.height + rot_h, rot_h + 120):
            for x in range(-rot_w, canvas.width + rot_w, rot_w + 120):
                overlay.paste(rotated, (x, y), rotated)
        return Image.alpha_composite(canvas, overlay)

    def _normalize_position(self, value, width: int, height: int, photo_width: int):
        if isinstance(value, str):
            if value == 'top-right':
                return (width - photo_width - 40, 60)
            if value == 'top-left':
                return (40, 60)
            if value == 'bottom-left':
                return (40, height - 120)
            if value == 'bottom-right':
                return (width - photo_width - 40, height - 120)
            if value == 'center':
                return (int((width - photo_width) / 2), int((height - photo_width) / 2))
        if isinstance(value, (list, tuple)) and len(value) == 2:
            try:
                return (int(value[0]), int(value[1]))
            except (ValueError, TypeError):
                pass
        return (80, 620)

    def create_flyer(self, product_image: Image.Image, caption: str, price_text: str, watermark: bool = False) -> bytes:
        width = self.config.get('width', 1080)
        height = self.config.get('height', 1080)
        canvas = Image.new('RGBA', (width, height), '#ffffff')
        canvas = self._apply_background(canvas)
        draw = ImageDraw.Draw(canvas)

        photo_width = self.config.get('photo_width', 520)
        photo_height = self.config.get('photo_height', 520)
        photo_x = self.config.get('photo_x', int((width - photo_width) / 2))
        photo_y = self.config.get('photo_y', 140)

        product_image = product_image.convert('RGBA')
        product_image = product_image.resize((photo_width, photo_height), Image.LANCZOS)
        
        if self.config.get('rounded_photo', False):
            product_image = self._round_corners(product_image, radius=30)
        
        if self.config.get('photo_shadow', True):
            shadowed = self._add_photo_shadow(product_image, offset=(6, 6), blur=12)
            canvas.paste(shadowed, (photo_x - 20, photo_y - 20), shadowed)
        else:
            canvas.paste(product_image, (photo_x, photo_y), product_image)

        price_font = self._get_font(self.config.get('price_size', 42))
        caption_font = self._get_font(self.config.get('caption_size', 32))
        
        price_color = self.config.get('price_color', '#FFD700')
        caption_color = self.config.get('text_color', '#FFFFFF')
        caption_width = self.config.get('caption_width', width - 160)
        line_height = self.config.get('caption_line_height', int(caption_font.size * 1.3))

        price_pos = self._normalize_position(self.config.get('price_position', (80, 620)), width, height, photo_width)
        caption_pos = self._normalize_position(self.config.get('caption_position', (80, 700)), width, height, photo_width)

        if self.config.get('text_bg', False):
            text_bg_color = self.config.get('text_bg_color', [0, 0, 0, 140])
            text_bg_padding = self.config.get('text_bg_padding', 20)
            try:
                lines = self._wrap_text(draw, caption, caption_font, caption_width)
                total_text_height = len(lines) * line_height + price_font.size + 30
                draw.rounded_rectangle(
                    [caption_pos[0] - text_bg_padding, caption_pos[1] - text_bg_padding,
                     caption_pos[0] + caption_width + text_bg_padding, caption_pos[1] + total_text_height + text_bg_padding],
                    radius=15, fill=tuple(text_bg_color)
                )
            except Exception:
                pass

        draw.text(price_pos, price_text, fill=price_color, font=price_font)
        
        lines = self._wrap_text(draw, caption, caption_font, caption_width)
        x, y = caption_pos
        for line in lines:
            draw.text((x, y), line, font=caption_font, fill=caption_color)
            y += line_height

        if self.config.get('accent_line', False):
            line_y = self.config.get('accent_line_y', caption_pos[1] - 30)
            draw.line((80, line_y, width - 80, line_y), fill=self.config.get('accent_color', '#D4AF37'), width=2)

        brand_mark = self.config.get('brand_mark', '')
        if brand_mark:
            small_font = self._get_font(14)
            draw.text((width - 100, height - 25), brand_mark, fill=(255, 255, 255, 100), font=small_font)

        if self.config.get('vignette', False):
            canvas = self._add_vignette(canvas)

        if watermark:
            canvas = self._add_watermark(canvas)

        output = io.BytesIO()
        canvas.convert('RGB').save(output, format='JPEG', quality=90)
        return output.getvalue()

    # ===================== GENERATIVE LAYOUT PATH =====================
    # Draws from a layout dict produced by layout_engine.generate_layout().
    # Kept separate from create_flyer() above so the original static
    # config-driven path keeps working untouched as a fallback.

    def _draw_background_from_layout(self, canvas: Image.Image, bg: dict) -> Image.Image:
        width, height = canvas.size
        colors = bg.get('colors') or ['#1a1a2e']
        if bg.get('type') == 'solid' or len(colors) == 1:
            return Image.new('RGBA', (width, height), colors[0])
        top_color, bottom_color = colors[0], colors[-1]
        for y in range(height):
            blend = y / (height - 1) if height > 1 else 0
            r = int(int(top_color[1:3], 16) * (1 - blend) + int(bottom_color[1:3], 16) * blend)
            g = int(int(top_color[3:5], 16) * (1 - blend) + int(bottom_color[3:5], 16) * blend)
            b = int(int(top_color[5:7], 16) * (1 - blend) + int(bottom_color[5:7], 16) * blend)
            ImageDraw.Draw(canvas).line([(0, y), (width, y)], fill=(r, g, b))
        return canvas

    def create_flyer_from_layout(self, product_image: Image.Image, caption: str, price_text: str,
                                  layout: dict, watermark: bool = False) -> bytes:
        width = height = 1080
        canvas = Image.new('RGBA', (width, height), '#ffffff')
        canvas = self._draw_background_from_layout(canvas, layout.get('background', {}))
        draw = ImageDraw.Draw(canvas)

        # --- accents drawn first so photo/text sit on top ---
        for accent in layout.get('accents', []):
            coords = accent.get('coords', [])
            color = accent.get('color', '#D4AF37')
            a_width = accent.get('width', 2)
            try:
                if accent.get('type') == 'line' and len(coords) == 4:
                    draw.line(coords, fill=color, width=a_width)
                elif accent.get('type') == 'rectangle' and len(coords) == 4:
                    draw.rectangle(coords, outline=color, width=a_width)
                elif accent.get('type') == 'circle' and len(coords) == 3:
                    cx, cy, r = coords
                    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=a_width)
            except Exception:
                continue

        # --- photo ---
        photo = layout.get('photo', {})
        p_w, p_h = photo.get('width', 500), photo.get('height', 500)
        p_x, p_y = photo.get('x', 290), photo.get('y', 140)
        product_image = product_image.convert('RGBA').resize((p_w, p_h), Image.LANCZOS)
        if photo.get('border_radius', 0) > 0:
            product_image = self._round_corners(product_image, radius=photo['border_radius'])
        if photo.get('shadow', True):
            shadowed = self._add_photo_shadow(product_image, offset=(6, 6), blur=12)
            canvas.paste(shadowed, (p_x - 20, p_y - 20), shadowed)
        else:
            canvas.paste(product_image, (p_x, p_y), product_image)

        # --- price ---
        # Semantic note: for typography-led skills (e.g. skill-quotes) this
        # field is repurposed as a short attribution/accent line rather than
        # a literal price -- hence the 'accent' role mapping below. Skills
        # without a typography block are unaffected; _get_typography_font()
        # falls straight through to _get_font() for them.
        price = layout.get('price', {})
        price_font = self._get_typography_font(layout, 'accent', price.get('size', 44))
        price_pos = (price.get('x', 80), price.get('y', 80))
        if price.get('bg_shape', 'none') != 'none':
            try:
                bbox = draw.textbbox(price_pos, price_text, font=price_font)
                pad = 14
                box = [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad]
                if price.get('bg_shape') == 'pill':
                    draw.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=price.get('bg_color', '#000000'))
                else:
                    draw.rectangle(box, fill=price.get('bg_color', '#000000'))
            except Exception:
                pass
        draw.text(price_pos, price_text, fill=price.get('color', '#FFD700'), font=price_font)

        # --- caption ---
        # The main wrapped text block -- the quote itself, for quote-type
        # skills -- so it takes the 'headline' role, the dominant font in
        # the pairing.
        caption_cfg = layout.get('caption', {})
        caption_font = self._get_typography_font(layout, 'headline', caption_cfg.get('size', 28))
        caption_pos = (caption_cfg.get('x', 80), caption_cfg.get('y', 700))
        max_width = caption_cfg.get('max_width', 920)
        line_height = caption_cfg.get('line_height', 38)
        lines = self._wrap_text(draw, caption, caption_font, max_width)

        if caption_cfg.get('bg_shape') == 'rounded_rect' and caption_cfg.get('bg_color'):
            try:
                total_h = len(lines) * line_height + 20
                pad = 20
                draw.rounded_rectangle(
                    [caption_pos[0] - pad, caption_pos[1] - pad,
                     caption_pos[0] + max_width + pad, caption_pos[1] + total_h + pad],
                    radius=15, fill=caption_cfg['bg_color']
                )
            except Exception:
                pass

        x, y = caption_pos
        for line in lines:
            draw.text((x, y), line, font=caption_font, fill=caption_cfg.get('color', '#FFFFFF'))
            y += line_height

        # --- brand mark ---
        brand = layout.get('brand_mark', {})
        if brand.get('text'):
            small_font = self._get_font(brand.get('size', 14))
            draw.text((brand.get('x', width - 110), brand.get('y', height - 30)),
                       brand['text'], fill=brand.get('color', '#FFFFFF64'), font=small_font)

        if watermark:
            canvas = self._add_watermark(canvas)

        output = io.BytesIO()
        canvas.convert('RGB').save(output, format='JPEG', quality=90)
        return output.getvalue()
