async function askAI() {

    const promptElement =
        document.getElementById("aiPrompt");

    const responseElement =
        document.getElementById("aiResponse");

    const prompt =
        promptElement.value.trim();

    if (!prompt) {

        responseElement.textContent =
            "Please enter a prompt.";

        return;
    }

    responseElement.textContent =
        "AI is thinking...";

    try {

        const response = await fetch(
            "/api/ai",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    prompt: prompt
                })
            }
        );

        const data =
            await response.json();

        if (!data.success) {

            responseElement.textContent =
                data.error ||
                "AI service unavailable.";

            return;
        }

        responseElement.textContent =
            data.response;

    } catch (error) {

        responseElement.textContent =
            "Unable to connect to the server.";
    }
}