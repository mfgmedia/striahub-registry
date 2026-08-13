"""Example activities for the hello-world project."""


def greet(config, input_data, ctx):
    """Greet someone by name."""
    prefix = config.get("prefix", "Hello")
    name = input_data["name"]
    greeting = f"{prefix}, {name}!"
    ctx.log("greeted", {"name": name, "greeting": greeting})
    return {"greeting": greeting}


def uppercase(config, input_data, ctx):
    """Convert text to uppercase."""
    text = input_data["text"]
    result = text.upper()
    ctx.log("shouted", {"original": text, "result": result})
    return {"text": result}
