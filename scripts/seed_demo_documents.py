"""Seed 10 demo documents for exploring document functionality.

Usage (from backend/):
    python ../scripts/seed_demo_documents.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlmodel import select  # noqa: E402
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: E402

from app.db.session import AdminSessionLocal  # noqa: E402
from app.models.document import (  # noqa: E402
    Document,
    DocumentLink,
    DocumentPermission,
    DocumentPermissionLevel,
    ProjectDocument,
)
from app.models.guild import Guild  # noqa: E402
from app.models.initiative import Initiative  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.tag import DocumentTag, Tag  # noqa: E402
from app.models.user import User  # noqa: E402

GUILD_ID = 6
INITIATIVE_ID = 6
CREATOR_ID = 3
PROJECT_ID = 2


def _doc(paragraphs: list[str]) -> dict:
    children = []
    for text in paragraphs:
        children.append({
            "children": [{"text": text, "type": "text"}],
            "type": "paragraph",
        })
    return {"root": {"children": children, "type": "root"}}


DEMO_DOCUMENTS = [
    {
        "title": "Требования к MVP гипотез-трекера",
        "paragraphs": [
            "Цель MVP — дать команде единое место для фиксации, оценки и продвижения продуктовых гипотез.",
            "Обязательные сценарии: создание гипотезы, смена статуса, привязка к проекту, комментарии и история изменений.",
            "Нефункциональные требования: мультигильдийность, RLS-изоляция данных, поддержка мобильного клиента.",
        ],
        "tags": ["Hyposys", "ToRnD"],
        "link_to_project": True,
    },
    {
        "title": "Исследование пользователей: интервью с PM",
        "paragraphs": [
            "Проведено 6 интервью с продакт-менеджерами из B2B SaaS-команд.",
            "Главная боль: гипотезы живут в Notion, Jira и таблицах — нет единого статуса и прозрачности для стейкхолдеров.",
            "Ожидаемый outcome: сократить время от идеи до решения «делаем / не делаем» на 30%.",
        ],
        "tags": ["Hyposys"],
    },
    {
        "title": "Архитектура: документы и совместное редактирование",
        "paragraphs": [
            "Документы хранятся в PostgreSQL (JSONB content + optional Yjs state для real-time collaboration).",
            "Доступ контролируется на уровне инициативы, ролей и персональных permissions (owner / write / read).",
            "Wikilinks между документами индексируются в document_links для отображения backlinks.",
        ],
        "tags": ["ToRnD"],
        "link_to_project": True,
    },
    {
        "title": "Гайд: жизненный цикл гипотезы",
        "paragraphs": [
            "Статусы: idea → evaluation → research → decision → project / rejected / paused.",
            "На этапе evaluation фиксируем критерии успеха и метрики. На research — собираем данные и ссылки на документы.",
            "Decision завершается явным исходом: запуск в проект, отказ или пауза с причиной.",
        ],
        "tags": ["Hyposys"],
    },
    {
        "title": "Спринт-планирование: июль 2026",
        "paragraphs": [
            "Фокус спринта: улучшение UX списка документов, поиск, фильтры по тегам и инициативам.",
            "Deliverables: глобальный scope документов, шаблоны, превью контента в карточках.",
            "Риски: производительность при большом количестве документов — нужна пагинация и виртуализация.",
        ],
        "tags": ["ToRnD"],
    },
    {
        "title": "Чеклист онбординга нового участника RnD",
        "paragraphs": [
            "1. Получить инвайт в гильдию RnD Team.",
            "2. Ознакомиться с инициативой «Гипозис Таск Трекер» и ключевыми проектами.",
            "3. Прочитать гайд по гипотезам и шаблон PRD перед созданием первого документа.",
        ],
        "tags": ["Hyposys", "ToRnD"],
    },
    {
        "title": "Протокол встречи: синк со стейкхолдерами",
        "paragraphs": [
            "Участники: Elizaveta, Geo, Danil. Дата: 10 июля 2026.",
            "Решения: приоритизировать документы как knowledge base для гипотез; добавить демо-данные для UX-ревью.",
            "Action items: подготовить 10 демо-документов, провести walkthrough по permissions и wikilinks.",
        ],
        "tags": ["Hyposys"],
    },
    {
        "title": "Конкурентный анализ: hypothesis management tools",
        "paragraphs": [
            "Рассмотрены: Productboard, Aha!, Notion databases, custom Airtable setups.",
            "Productboard силён в roadmap, но слаб в гибкой методологии гипотез для небольших команд.",
            "Наше преимущество: гильдии, инициативы, задачи и документы в одной системе с RLS.",
        ],
        "tags": ["ToRnD"],
    },
    {
        "title": "Спецификация API: документы",
        "paragraphs": [
            "POST /api/v1/documents/ — создание документа в инициативе с owner permission для автора.",
            "GET /api/v1/documents/?scope=global — документы текущего пользователя across guilds.",
            "PATCH /api/v1/documents/{id} — обновление title, content, featured_image_url, is_template.",
        ],
        "tags": ["ToRnD"],
        "link_to_project": True,
    },
    {
        "title": "Шаблон PRD",
        "paragraphs": [
            "## Проблема",
            "Опишите пользовательскую боль и контекст.",
            "## Решение",
            "Кратко сформулируйте предлагаемое решение.",
            "## Метрики успеха",
            "Как поймём, что гипотеза подтвердилась?",
            "## Out of scope",
            "Что сознательно не входит в первую итерацию.",
        ],
        "tags": ["Hyposys"],
        "is_template": True,
    },
]

DOCUMENT_LINKS = [
    ("Требования к MVP гипотез-трекера", "Гайд: жизненный цикл гипотезы"),
    ("Требования к MVP гипотез-трекера", "Шаблон PRD"),
    ("Исследование пользователей: интервью с PM", "Требования к MVP гипотез-трекера"),
    ("Архитектура: документы и совместное редактирование", "Спецификация API: документы"),
    ("Чеклист онбординга нового участника RnD", "Гайд: жизненный цикл гипотезы"),
    ("Чеклист онбординга нового участника RnD", "Шаблон PRD"),
    ("Протокол встречи: синк со стейкхолдерами", "Спринт-планирование: июль 2026"),
]


async def _get_or_fail(session: AsyncSession) -> tuple[Guild, Initiative, User, Project | None]:
    guild = await session.get(Guild, GUILD_ID)
    initiative = await session.get(Initiative, INITIATIVE_ID)
    creator = await session.get(User, CREATOR_ID)
    project = await session.get(Project, PROJECT_ID)

    if not guild:
        raise RuntimeError(f"Guild {GUILD_ID} not found")
    if not initiative or initiative.guild_id != guild.id:
        raise RuntimeError(f"Initiative {INITIATIVE_ID} not found in guild {GUILD_ID}")
    if not creator:
        raise RuntimeError(f"User {CREATOR_ID} not found")

    return guild, initiative, creator, project


async def seed_demo_documents() -> None:
    async with AdminSessionLocal() as session:
        guild, initiative, creator, project = await _get_or_fail(session)

        result = await session.exec(
            select(Tag).where(Tag.guild_id == guild.id)
        )
        tags_by_name = {tag.name: tag for tag in result.all()}

        existing_titles = set(
            await session.exec(
                select(Document.title).where(
                    Document.guild_id == guild.id,
                    Document.initiative_id == initiative.id,
                )
            )
        )

        created: dict[str, Document] = {}
        skipped = 0

        for spec in DEMO_DOCUMENTS:
            title = spec["title"]
            if title in existing_titles:
                print(f"  skip (exists): id pending")
                skipped += 1
                continue

            doc = Document(
                guild_id=guild.id,
                initiative_id=initiative.id,
                title=title,
                content=_doc(spec["paragraphs"]),
                created_by_id=creator.id,
                updated_by_id=creator.id,
                is_template=spec.get("is_template", False),
            )
            session.add(doc)
            await session.flush()

            session.add(
                DocumentPermission(
                    document_id=doc.id,
                    user_id=creator.id,
                    guild_id=guild.id,
                    level=DocumentPermissionLevel.owner,
                )
            )

            for tag_name in spec.get("tags", []):
                tag = tags_by_name.get(tag_name)
                if tag:
                    session.add(DocumentTag(document_id=doc.id, tag_id=tag.id))

            if spec.get("link_to_project") and project and project.guild_id == guild.id:
                session.add(
                    ProjectDocument(
                        project_id=project.id,
                        document_id=doc.id,
                        guild_id=guild.id,
                        attached_by_id=creator.id,
                    )
                )

            created[title] = doc
            print(f"  created: id={doc.id}")

        for source_title, target_title in DOCUMENT_LINKS:
            source = created.get(source_title)
            target = created.get(target_title)
            if not source or not target:
                continue
            session.add(
                DocumentLink(
                    source_document_id=source.id,
                    target_document_id=target.id,
                    guild_id=guild.id,
                )
            )

        await session.commit()

        print()
        print(f"Done: {len(created)} created, {skipped} skipped.")
        print(f"Guild id={guild.id}")
        print(f"Initiative id={initiative.id}")
        print(f"Owner id={creator.id}")


if __name__ == "__main__":
    print("Seeding demo documents...")
    asyncio.run(seed_demo_documents())
