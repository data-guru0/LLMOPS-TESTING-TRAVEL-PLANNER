# Importing ChatGroq from langchain_groq to use the Groq-hosted LLM (like LLaMA 3)
from langchain_groq import ChatGroq

# Importing ChatPromptTemplate to create a structured prompt for the LLM
from langchain_core.prompts import ChatPromptTemplate

# Importing the GROQ_API_KEY from config file (stored securely in .env)
from src.config.config import GROQ_API_KEY

# Creating an instance of the ChatGroq model with specific settings
llm = ChatGroq(
    temperature=0,                    # temperature = 0 means the model will be deterministic (same output for same input)
    groq_api_key=GROQ_API_KEY,        # using the API key we stored securely in .env
    model_name="llama-3.3-70b-versatile"  # choosing the LLaMA 3.3 model variant from Groq
)

# Creating a prompt template that tells the model what we want it to do
itinerary_prompt = ChatPromptTemplate.from_messages([
    # This is a system message that gives the model instructions about its role
    ("system", "You are a helpful travel assistant. Create a day trip itinerary for {city} based on the user's interests: {interests}. Provide a brief, bulleted itinerary."),
    
    # This is a simulated human message that acts as the starting point of the chat
    ("human", "Create an itinerary for my day trip."),
])

# This function generates the itinerary using the model based on the user's city and interests
def generate_itinerary(city: str, interests: list[str]) -> str:
    # Sending the formatted prompt to the model and storing the response
    response = llm.invoke(
        itinerary_prompt.format_messages(
            city=city,                          # replacing {city} in prompt with actual city
            interests=', '.join(interests)      # joining the list of interests into a single string
        )
    )
    # Returning only the textual content from the model's response
    return response.content
