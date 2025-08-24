from g4f.Provider import CohereForAI_C4AI_Command
import g4f

from random import choice
import sys
import io


def create_comment(text: str) -> list:
    stdout_original = sys.stdout
    sys.stdout = io.StringIO()

    response = g4f.ChatCompletion.create(
        model='command-r7b',
        provider=CohereForAI_C4AI_Command,
        messages=[
            {"role": "user", "content": f"""
Ты — эксперт по переформулированию текста. 
Твоя цель — уникализировать комментарий так, чтобы он выглядел по-новому, но при этом смысл оставался полностью сохранён. 

Инструкции:
1. Прочитай исходный комментарий.  
2. Сохрани общий смысл и тональность.  
3. Сгенерируй ровно 3 уникальных варианта.  
4. Каждый вариант должен отличаться по структуре, лексике и длине.  
5. Выведи результат строго в одной строке через символ "|" без вступлений, пояснений, номеров и двоеточий.  
6. Выводи только Комментарии, ничего не объясняй

Комментарий: {text}

Вывод (строго в формате):
Комментарий 1 | Комментарий 2 | Комментарий 3
"""}])

    sys.stdout = stdout_original
    result = response.split("|")

    return choice(result).rstrip()
