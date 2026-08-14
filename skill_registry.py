import json
from pathlib import Path
from typing import Dict, Any

from config import SKILLS_PATH


class SkillRegistry:
    def __init__(self, skills_path: Path = SKILLS_PATH):
        self.skills_path = Path(skills_path)
        self.graphic_skills: Dict[str, Dict[str, Any]] = {}
        self.prompt_skills: Dict[str, Dict[str, Any]] = {}
        self.category_skills: Dict[str, Dict[str, Any]] = {}
        self.load_skills()

    def _load_skill_metadata(self, skill_dir: Path) -> Dict[str, Any]:
        config_path = skill_dir / 'config.json'
        if not config_path.exists():
            return {}
        with config_path.open('r', encoding='utf-8') as fh:
            return json.load(fh)

    def _load_skill_examples(self, skill_dir: Path) -> list:
        examples_path = skill_dir / 'examples.json'
        if not examples_path.exists():
            return []
        with examples_path.open('r', encoding='utf-8') as fh:
            return json.load(fh)

    def _load_skill_vocab(self, skill_dir: Path) -> Dict[str, Any]:
        vocab_path = skill_dir / 'vocabulary.json'
        if not vocab_path.exists():
            return {}
        with vocab_path.open('r', encoding='utf-8') as fh:
            return json.load(fh)

    def _load_skill_constraints(self, skill_dir: Path) -> Dict[str, Any]:
        constraints_path = skill_dir / 'constraints.json'
        if not constraints_path.exists():
            return {}
        with constraints_path.open('r', encoding='utf-8') as fh:
            return json.load(fh)

    def load_skills(self):
        graphic_dir = self.skills_path / 'graphic'
        prompt_dir = self.skills_path / 'prompt'
        category_dir = self.skills_path / 'category'

        for skill_dir in graphic_dir.glob('*'):
            if not skill_dir.is_dir():
                continue
            metadata = self._load_skill_metadata(skill_dir)
            self.graphic_skills[skill_dir.name] = {
                'name': metadata.get('name', skill_dir.name),
                'description': metadata.get('description', ''),
                'skill_dir': skill_dir,
                'template': str(skill_dir / metadata.get('template', 'template.png')),
                'config': metadata,
            }

        for skill_dir in prompt_dir.glob('*'):
            if not skill_dir.is_dir():
                continue
            metadata = self._load_skill_metadata(skill_dir)
            self.prompt_skills[skill_dir.name] = {
                'name': metadata.get('name', skill_dir.name),
                'description': metadata.get('description', ''),
                'skill_dir': skill_dir,
                'config': metadata,
                'examples': self._load_skill_examples(skill_dir),
                'vocabulary': self._load_skill_vocab(skill_dir),
                'constraints': self._load_skill_constraints(skill_dir),
            }

        for skill_dir in category_dir.glob('*'):
            if not skill_dir.is_dir():
                continue
            metadata = self._load_skill_metadata(skill_dir)
            self.category_skills[skill_dir.name] = {
                'name': metadata.get('name', skill_dir.name),
                'description': metadata.get('description', ''),
                'skill_dir': skill_dir,
                'config': metadata,
            }

    def get_graphic_skill(self, name: str) -> Dict[str, Any] | None:
        return self.graphic_skills.get(name)

    def get_prompt_skill(self, name: str) -> Dict[str, Any] | None:
        return self.prompt_skills.get(name)

    def get_category_skill(self, name: str) -> Dict[str, Any] | None:
        return self.category_skills.get(name)

    def list_graphic_skills(self) -> list:
        return list(self.graphic_skills.keys())

    def list_prompt_skills(self) -> list:
        return list(self.prompt_skills.keys())

    def list_category_skills(self) -> list:
        return list(self.category_skills.keys())

    def choose_graphic_skill(self, customer: dict, product_description: str | None = None) -> str:
        preferred = customer.get('preferred_graphic_skill')
        if preferred and preferred in self.graphic_skills:
            return preferred

        text = (product_description or '').lower()
        weights: dict[str, int] = {}

        for name, skill in self.graphic_skills.items():
            config = skill.get('config', {})
            tags = [t.lower() for t in config.get('tags', [])]
            keywords = [t.lower() for t in config.get('keywords', [])]
            score = 0
            for term in tags + keywords:
                if term in text:
                    score += 2
            for term in ['sale', 'discount', 'flash', 'limited', 'promo', 'today', 'urgent']:
                if term in text and name == 'skill-urgency':
                    score += 3
            for term in ['party', 'holiday', 'christmas', 'eid', 'valentine', 'detty', 'celebration']:
                if term in text and name == 'skill-festive':
                    score += 3
            for term in ['corporate', 'office', 'service', 'professional', 'business', 'church']:
                if term in text and name == 'skill-minimal':
                    score += 3
            for term in ['street', 'fast', 'trendy', 'youth', 'vibe']:
                if term in text and name == 'skill-bold':
                    score += 3
            weights[name] = score

        if weights:
            best = max(weights, key=weights.get)
            if weights.get(best, 0) > 0:
                return best

        return 'skill-luxury'

    def choose_prompt_skill(self, customer: dict) -> str:
        return customer.get('preferred_prompt_skill') or 'skill-english-market'

    def choose_category_skill(self, customer: dict, niche: str | None = None) -> str:
        preferred = customer.get('preferred_category_skill')
        if preferred and preferred in self.category_skills:
            return preferred
        text = (niche or '').lower()
        mapping = {
            'fashion': 'skill-fashion',
            'cloth': 'skill-fashion',
            'beauty': 'skill-beauty',
            'cosmetic': 'skill-beauty',
            'skincare': 'skill-beauty',
            'food': 'skill-food',
            'cake': 'skill-food',
            'snack': 'skill-food',
            'retail': 'skill-retail',
            'furniture': 'skill-retail',
            'phone': 'skill-retail',
            'church': 'skill-church',
            'crusade': 'skill-church',
            'convention': 'skill-church',
            'ministry': 'skill-church',
            'fellowship': 'skill-church',
            'choir': 'skill-church',
            'jersey': 'skill-sports',
            'football': 'skill-sports',
            'sportswear': 'skill-sports',
            'gym': 'skill-sports',
            'fitness': 'skill-sports',
            'sneaker': 'skill-sports',
            'tracksuit': 'skill-sports',
        }
        for key, val in mapping.items():
            if key in text:
                return val
        return 'skill-retail'
