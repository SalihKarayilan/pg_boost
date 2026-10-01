import asyncio
import streamlit as st
import google.generativeai as genai
from utils.prompts import SYSTEM_INSTRUCTION, build_user_message

def perform_analysis(provider_choice, model_choice, api_key, sql_query, ddl_info, explain_output):
    user_message = build_user_message(ddl_info, sql_query, explain_output)

    async def fetch_analysis():
        try:
            if provider_choice == "Gemini":
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=model_choice,
                    system_instruction=SYSTEM_INSTRUCTION
                )
                response = await model.generate_content_async(user_message)
                return response.text

            elif provider_choice == "OpenAI":
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=api_key)
                response = await client.chat.completions.create(
                    model=model_choice,
                    messages=[
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": user_message}
                    ]
                )
                return response.choices[0].message.content

            elif provider_choice == "Claude":
                from anthropic import AsyncAnthropic
                client = AsyncAnthropic(api_key=api_key)
                response = await client.messages.create(
                    model=model_choice,
                    system=SYSTEM_INSTRUCTION,
                    messages=[
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=1024
                )
                return response.content[0].text
        except Exception as e:
            st.error(f"Bir hata oluştu: {str(e)}")
            return None

    return asyncio.run(fetch_analysis())
