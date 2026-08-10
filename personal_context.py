import json
import re
from config import PERSONAL_PROFILE_JSON

FINANCE_WORDS = {
    "uang", "gaji", "gapok", "insentif", "ekonomi", "keuangan", "modal", "usaha",
    "bisnis", "penghasilan", "income", "cuan", "tabungan", "sewa", "kontrakan", "utang",
    "freelance", "affiliate", "afiliasi", "side hustle", "kerja sampingan", "karier", "career"
}
FAMILY_WORDS = {
    "keluarga", "istri", "anak", "shafa", "zein", "fitri", "rumah", "kontrakan", "ayah", "orang tua"
}
HEALTH_WORDS = {
    "sehat", "kesehatan", "sakit", "paru", "infeksi", "udara", "dokter", "batuk", "demam", "bpjs", "asuransi"
}
WORK_WORDS = {
    "kerja", "kantor", "mrm", "daihatsu", "desain", "design", "motion", "video", "editing",
    "kamera", "kameramen", "videografer", "talent", "konten", "sosmed", "website", "web", "portofolio",
    "freelance", "client", "klien", "branding", "marketing"
}


def load_profile():
    if not PERSONAL_PROFILE_JSON:
        return {}
    try:
        data = json.loads(PERSONAL_PROFILE_JSON)
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        print("PERSONAL_PROFILE_JSON invalid:", repr(exc))
        return {}


def _contains_any(text, words):
    low = (text or "").lower()
    return any(word in low for word in words)


def _fmt_list(values):
    if not values:
        return ""
    if isinstance(values, str):
        return values
    return ", ".join(str(x) for x in values if x)


def build_personal_context(user_text=""):
    """Return only the profile sections relevant to the current request.

    Sensitive family/health/finance details are not sprayed into every model request.
    """
    p = load_profile()
    if not p:
        return ""

    lines = ["KONTEKS PERSONAL USER (gunakan secara bijak, jangan diulang tanpa alasan):"]

    name = p.get("name")
    age = p.get("age")
    if name:
        lines.append(f"- Nama: {name}" + (f", usia {age} tahun" if age else ""))

    work = p.get("work") or {}
    if work:
        company = work.get("company")
        role = work.get("role")
        skills = _fmt_list(work.get("skills"))
        if company or role:
            lines.append(f"- Pekerjaan utama: {role or '-'} di {company or '-'}")
        if skills:
            lines.append(f"- Skill utama: {skills}")

    goals = _fmt_list(p.get("goals"))
    if goals:
        lines.append(f"- Tujuan: {goals}")

    career = p.get("career_history") or []
    if career and (_contains_any(user_text, WORK_WORDS) or _contains_any(user_text, FINANCE_WORDS)):
        lines.append("- Riwayat/pengalaman relevan:")
        for item in career[:12]:
            if isinstance(item, dict):
                org = item.get("organization", "")
                role = item.get("role", "")
                note = item.get("note", "")
                period = item.get("period", "")
                lines.append(f"  • {org}: {role}" + (f" ({period})" if period else "") + (f" — {note}" if note else ""))
            else:
                lines.append(f"  • {item}")

    if _contains_any(user_text, FAMILY_WORDS | HEALTH_WORDS | FINANCE_WORDS):
        family = p.get("family") or {}
        spouse = family.get("spouse") or {}
        children = family.get("children") or []
        if spouse:
            lines.append(f"- Istri: {spouse.get('name','-')}" + (f", {spouse.get('age')} tahun" if spouse.get("age") else ""))
        if children:
            parts = []
            for child in children:
                desc = child.get("name", "anak")
                if child.get("age"):
                    desc += f" ({child.get('age')})"
                if child.get("gender"):
                    desc += f", {child.get('gender')}"
                parts.append(desc)
            lines.append("- Anak: " + "; ".join(parts))

    if _contains_any(user_text, HEALTH_WORDS):
        health = p.get("health_context") or []
        if health:
            lines.append("- Konteks kesehatan keluarga yang relevan: " + _fmt_list(health))

    if _contains_any(user_text, FINANCE_WORDS):
        finance = p.get("finance") or {}
        if finance:
            if finance.get("base_salary"):
                lines.append(f"- Penghasilan tetap: {finance['base_salary']}")
            if finance.get("incentive"):
                lines.append(f"- Insentif: {finance['incentive']}")
            if finance.get("rent"):
                lines.append(f"- Sewa tempat tinggal: {finance['rent']}")
            benefits = _fmt_list(finance.get("benefits"))
            if benefits:
                lines.append(f"- Benefit kantor: {benefits}")
            if finance.get("constraint"):
                lines.append(f"- Kondisi cashflow: {finance['constraint']}")

    principles = _fmt_list(p.get("decision_principles"))
    if principles:
        lines.append(f"- Prinsip keputusan: {principles}")

    return "\n".join(lines)


def build_digest_profile():
    """Non-health profile for daily opportunity/news ranking."""
    p = load_profile()
    if not p:
        return ""
    work = p.get("work") or {}
    lines = []
    if p.get("name"):
        lines.append(f"Nama: {p['name']}")
    if work.get("role") or work.get("company"):
        lines.append(f"Pekerjaan: {work.get('role','')} di {work.get('company','')}")
    skills = _fmt_list(work.get("skills"))
    if skills:
        lines.append(f"Skill: {skills}")
    goals = _fmt_list(p.get("goals"))
    if goals:
        lines.append(f"Tujuan: {goals}")
    return "\n".join(lines)


def profile_summary():
    p = load_profile()
    if not p:
        return "Profil personal belum dikonfigurasi."
    work = p.get("work") or {}
    return (
        f"Profil aktif untuk {p.get('name','user')}. "
        f"Fokus: {work.get('role','pekerjaan kreatif')}; "
        f"tujuan: {_fmt_list(p.get('goals')) or 'belum diisi'}."
    )
