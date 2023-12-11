import asyncio
import sys

from app.openai import call_openai


async def main() -> None:
    input = sys.argv[1]
    # TODO: read input from a text file
    res = await call_openai(
        messages=[{"role": "user", "content": input}], model="gpt-4"
    )
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
