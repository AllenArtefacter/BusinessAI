# GPT Data Analyst

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]()

This app utilizes chatGPT API to introspect a DB and query it using user's prompt. It also utilizes Streamlit as simple UI.


## Contribution

### Pricing

https://community.openai.com/t/gpt4-and-gpt-3-5-turb-api-cost-comparison-and-understanding/106192
https://openai.com/pricing

#### GPT 4

On the demo dataset it cost between 0.05$ and 0.10$ / request, depending on the configuration and input.
and I would disabled for the tiktok dataset for now because the price could go up to 0.27$ with current 
configuration

```
>>> 800*0.00003+500*0.00006
0.054
>>> 2000*0.00003+1000*0.00006
0.120
>>> 7000*0.00003+1000*0.00006
0.27
```


#### GPT 3.5 turbo

```
>>> 3000*0.000002
0.006
```

~20 times cheaper

### Github Actions

To pass github actions tests
- Format the code using 
```bash
black .
```
- Order the import using 
```bash
isort . --profile black
```

## Architecture choices

Conversation:
    list[Chats]
        list[Messages]
            type = ai, human, system
            content
            code
            input
                

### Rules

- The app uses streamlit but do not include streamlit in files likely to also be used in non-streamlit usages

### Main Idea

One idea would be to have some sort of free gpt able to choose when to display a dataframe/number and when to plot.
However, doing this implies either :
- to add the choice in the current prompt leading to a more complex prompt and worse results overall for complex tasks
- One more model defining what to do ahead leading to more time to compute
- Often the user will know what he wants to do so it is better to let him choose

### Plotting

- Plotting adds to the prompt to it should be a separate function not to overcomplicate the prompt
- This should work with streamlit so the easiest library to use is ?

## Masking

1. Sets generation
2. Word-level mapping
3. Replacement

Since the level of mapping is static, the addition of new sentences/words won't change the mapping.
It should only change the masks if a new context is given to an already masked word.

When a masked dataset is generated it can be kept and reused for the same context.
The word maps can also be saved and reused for the same context.

## DataLoader

init(data_folder_name, transformers: list[Transformers])
from_folder(folder_name) -> creates 

get_data() -> dict[str, pd.DataFrame]
get_transformed_data() -> dict[str, pd.DataFrame]
get_columns() -> dict[str, list[str]]
get_transformed_columns() -> dict[str, list[str]]
get_table_names() -> list[str]

_transform() -> call all transform methods on the data
        In the case of the Masker(Transformer)
            - mask the data
- saves the transformed data 
- saves the masker transformers{for_each}.save(folder)


folder architecture (in project_root/res/data)
- data_name
  - *.[csv, xlsx] (raw datasets)
  - transformed.pkl (transformed datasets (dict))
  - transformer.pll (TODO)


## New dataset import

create a new folder and copy the files in it.

## Behavior on gpt reply

- If the reply is a code, it is executed and the result is displayed
- Does contains "question: " -> ask the question to the user and highlight the reply button
- neither code nor question -> assume he is going to continue writing, auto ask "continue writing the code"

To do so we wait for the message to be in the chat and then we check the last message. The last message from AI can 
have a state
- 'OK': The code was executed and the result is displayed
- 'ASK': The question has to be asked to the user before continuing
- 'CONTINUE': gpt is automatically prompted to continue writing the code


## Running streamlit app
- On streamlit server(directly connected with GitHub): you need to provide the secrets in format of `OPENAI_API_KEY="sk-xxxx"`
- On local/server: Update `OPENAI_API_KEY` in `.streamlit/secrets_template.toml`