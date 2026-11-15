from typing import Any
from datetime import date

from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.db import connection
from django.db.models import QuerySet
from django.test.utils import CaptureQueriesContext

from apps.blogs.queries import QUERIES
from apps.auths.models import User


def query(function):
    """Decorator to return number of executed queries and list of executed SQL queries"""

    MAX_RESULT_LENGTH: int = 5

    def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:

        with CaptureQueriesContext(connection) as context:
            result = function(*args, **kwargs)

            if isinstance(result, QuerySet):
                evaluated_result = list(result)
            else:
                evaluated_result = result

            try:
                sliced_result = evaluated_result[:MAX_RESULT_LENGTH]
            except (TypeError, AttributeError, KeyError):
                sliced_result = evaluated_result

            query_count = len(context.captured_queries)     
            captured_queries = context.captured_queries  

        return {
            "result": sliced_result,
            "query_count": query_count,
            "captured_queries": [query["sql"] for query in captured_queries]
        }

    return wrapper


class Command(BaseCommand):
    """Command to queries.py queries"""

    # DEFAULT_QUERY: int = 1
    MAX_QUERY_NUMBER: int = 50
    EXCLUDE_QUERIES_RANGE: range = range(40, 45)
    SAMPLE_VALUES: dict[int, dict[str, Any]] = {
        4: {
            "slug": "point-chair-center"
        },
        7: {
            "page": 2
        },
        8: {
            "word": "any"
        },
        9: {
            "domain": "kbtu.kz"
        },
        11: {
            "slugs": ["python", "django", "databases"]
        },
        12: {
            "year": 2026, 
            "month": 8
        },
        13: {
            "days": 7
        }, 
        14: {
            "start": date(2026, 8, 1),
            "end": date(2026, 10, 1)
        },
        15: {
            "email": User.objects.last()
        },
        16: {
            "tag_slug": "rest-api"
        },
        17: {
            "category_slug": "django"
        },
        21: {
            "first_slug": "redis",
            "second_slug": "celery"
        },
        22: {
            "text": "Free"
        },
        34: {
            "min_posts": 5
        },
        37: {
            "text": "vid s"
        },
        40: {
            "name": "Kotlin"
        },
        41: {
            "days": 10,
        },
        42: {
            "category_slug": "devops",
            "tag_slug": "postgresql"
        },
        43: {
            "source_slug": "testing",
            "target_slug": "security"
        }
    }

    help = "Execute queries.py file queries"

    @query
    def __execute_query(self, number: int) -> Any:
        """Execute <number> query from apps.blogs.queries.py"""

        if number in self.SAMPLE_VALUES:
            return QUERIES[number](**self.SAMPLE_VALUES[number])
        return QUERIES[number]()

    def __run_one(self, number: int, show_sql: bool = False) -> None:
        """Output single query result"""

        output = self.__execute_query(number)
        self.stdout.write(
            self.style.SUCCESS(f"#{number} {QUERIES[number].__name__} - {output['query_count']} SQL QUERY")
        )
        self.stdout.write(
            f"RESULT: {repr(output["result"])}"
        )
        self.stdout.write("\n")
        if show_sql:
            self.stdout.write(
                "\n".join([query for query in output["captured_queries"]])
            )
        self.stdout.write("\n")

    def add_arguments(self, parser: CommandParser) -> None:
        """Read arguments"""

        parser.add_argument(
            "--number",
            type=int,
            # default=self.DEFAULT_QUERY,
            help="Number of query to execute",
        )
        parser.add_argument(
            "--sql", action="store_true", help="Print the executed SQL query"
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        """Command entry point"""

        number: int = options["number"]
        show_sql: bool = options["sql"]

        self.stdout.write(self.style.NOTICE(f"{number=}, {show_sql=}"))

        if number:
            if number <= 0 or number > self.MAX_QUERY_NUMBER:
                raise CommandError("Number is out of range")
            self.__run_one(number, show_sql)
            return


        for curr_number in QUERIES:
            if curr_number not in self.EXCLUDE_QUERIES_RANGE:
                self.__run_one(curr_number, show_sql)