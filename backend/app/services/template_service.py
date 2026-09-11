import re
from typing import Dict, Any, List, Tuple

VARIABLE_REGEX = re.compile(r"\{([a-zA-Z0-9_]+)\}")

class TemplateService:
    @staticmethod
    def extract_variables(text: str) -> List[str]:
        """
        Extract all variable names enclosed in {var_name} from body or subject.
        """
        if not text:
            return []
        matches = VARIABLE_REGEX.findall(text)
        return list(dict.fromkeys(matches))  # preserve order & unique

    @staticmethod
    def render_template(template_str: str, data: Dict[str, Any]) -> str:
        """
        Safely replace placeholders like {name}, {subject}, {email}, or dynamic custom fields.
        If a variable is missing in data, it is left untouched or replaced with empty string gracefully.
        """
        if not template_str:
            return ""

        def replace_match(match):
            var_name = match.group(1)
            # Check case-insensitive match in data dictionary
            val = None
            for key, v in data.items():
                if key.lower() == var_name.lower():
                    val = v
                    break
            
            if val is not None:
                return str(val)
            return match.group(0) # Keep original tag if not found instead of raising KeyError

        return VARIABLE_REGEX.sub(replace_match, template_str)

    @staticmethod
    def preview(subject_template: str, body_template: str, sample_data: Dict[str, Any]) -> Tuple[str, str, List[str]]:
        rendered_subject = TemplateService.render_template(subject_template, sample_data)
        rendered_body = TemplateService.render_template(body_template, sample_data)
        vars_subject = TemplateService.extract_variables(subject_template)
        vars_body = TemplateService.extract_variables(body_template)
        all_vars = list(dict.fromkeys(vars_subject + vars_body))
        return rendered_subject, rendered_body, all_vars

