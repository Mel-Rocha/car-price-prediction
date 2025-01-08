import re

def validate_torque(torque: str) -> bool:
    """
    Valida se o torque está no formato esperado.
    Formatos válidos:
        - '250Nm@4500rpm'
        - '190Nm@ 2000rpm' (com espaço após o '@')
        - '350Nm@1750-2500rpm'
        - '51Nm@4000+/-500rpm'
        - '350Nm'
        - '4500rpm'
    """
    if not isinstance(torque, str) or not torque.strip():
        return False

    # Regex para os formatos válidos
    pattern = r"^\d+(?:\.\d+)?Nm(@\s?\d+(?:-\d+)?rpm)?$|^\d+rpm$|^\d+(?:\.\d+)?kgm(@\s?\d+(?:-\d+)?rpm)?$|^\d+(?:\.\d+)?Nm@4000\+/-\d+rpm$"
    return bool(re.match(pattern, torque))