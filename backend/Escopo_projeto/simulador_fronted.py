from chat import llm

def main():
    print(' ##########', '\n','Bem vindo ao chat','\n','##########')
    chain = llm()
    while True:
        user_input = input("Você: ")
        if user_input == "sair":
            break
        answer = chain.invoke({"input": user_input},
                                config={
                                    "configurable": {"session_id": "abc123"}
                                },  # constructs a key "abc123" in `store`.
                            )["answer"]
        print("Chatbot:", answer)

if __name__ == "__main__":
    main()