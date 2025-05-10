from dotenv import load_dotenv

def initialize_environment(dotenv_path: str | None = None) -> None:
  """Load environment variables from .env file.

  Args:
      dotenv_path: Optional path to the .env file. If not provided, will look in current directory.
  """
  if dotenv_path:
    load_dotenv(dotenv_path)
  else:
    load_dotenv()

def multiply(a: int, b: int) -> int:
  """Multiply a and b.

  Args:
      a: first int
      b: second int
  """
  return a * b


# This will be a tool
def add(a: int, b: int) -> int:
  """Adds a and b.

  Args:
      a: first int
      b: second int
  """
  return a + b


def divide(a: int, b: int) -> float:
  """Divide a and b.

  Args:
      a: first int
      b: second int
  """
  return a / b

def hello() -> str:
    return "Hello from mylibrary!"

def shit() -> str:
  return "Shit from mylibrary!"

def hell() -> str:
  return "Hello from hell!"
