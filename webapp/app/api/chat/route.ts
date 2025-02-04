import { semanticSearch } from "@/lib/ragSearch";
import { openai } from "@ai-sdk/openai";
import { streamText, generateObject } from "ai";
import { z } from "zod";

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai("gpt-4o"),
    system:
      "You are a helpful assistant that can answer questions about history. Answer only about the history of wars, nothing else. Politly decline to answer questions that are not about history of wars. You can use the searchWarsInfo tool to search into the database of HistoryAI for relevant information. When you have the answer, answer in the user's language in markdown format.",
    messages,
    maxSteps: 5,
    experimental_toolCallStreaming: true,
    toolChoice: "auto",
    tools: {
      searchWarsInfo: {
        description:
          "Searches similar documents in the user's documents provided into HistoryAI for relevant information. You can do multiple searches one after the other to get more results and go more in depth of a subject. The database is in french so your queries should be in french too.",
        parameters: z.object({
          query: z.string(),
        }),
        execute: async ({ query }) => {
          console.log("🔍 [Tool - searchWarsInfo] Query:", query);
          try {
            const searchResults = await semanticSearch(query);
            console.log(
              "✅ [Tool - searchWarsInfo] Résultats trouvés:",
              searchResults?.length
            );

            // Format les résultats avec une limite de contenu
            const formattedResults = searchResults?.map((result) => {
              // Limiter le contenu à environ 1000 caractères
              if (result.full_content) {
                const truncatedContent =
                  result.full_content?.length > 10000
                    ? result.full_content?.substring(0, 10000) +
                      "... (contenu tronqué)"
                    : result.full_content;

                return `# ${result.name}

## Contenu de la page wikepédia
${truncatedContent}

${result.url ? `[Voir le document complet](${result.url})` : ""}`;
              }
            });

            // Limiter le nombre de résultats à 3 maximum
            return formattedResults?.slice(0, 3);
          } catch (error) {
            console.error("❌ [Tool - searchWarsInfo] Erreur:", error);
            throw error;
          }
        },
      },
      generateQuiz: {
        description:
          "Génère un quiz éducatif structuré sur les guerres historiques en utilisant des informations vérifiées.",
        parameters: z.object({
          question: z
            .string()
            .describe("Question de l'utilisateur pour contextualiser le quiz"),
          lang: z
            .string()
            .default("fr")
            .describe("Langue de sortie pour le quiz"),
        }),
        execute: async ({ question, lang }, { messages }) => {
          try {
            const { object: quizData } = await generateObject({
              model: openai("gpt-4o"),
              schema: z.object({
                quiz: z.object({
                  title: z.string(),
                  questions: z
                    .array(
                      z.object({
                        question: z.string(),
                        options: z.array(z.string()).length(4),
                        correctAnswer: z.string(),
                      })
                    )
                    .min(3)
                    .max(10),
                }),
              }),
              system: `Expert en histoire militaire. Génère un quiz cohérent basé sur l'historique de conversation et les données vérifiées. 
                      Considère le contexte suivant: ${messages
                        .map((m) => m.content)
                        .join("\n")}
                      Structure les questions avec 4 options et une réponse claire.`,
              messages: [
                ...messages,
                {
                  role: "user",
                  content: `Crée un quiz sur: ${question} (Langue: ${lang})`,
                },
              ],
            });

            return {
              quiz: {
                ...quizData.quiz,
                questions: quizData.quiz.questions.map((q) => ({
                  ...q,
                  // Mélange les options et trouve l'index correct
                  options: shuffleArray(q.options),
                  correctIndex: q.options.indexOf(q.correctAnswer),
                })),
              },
            };
          } catch (error) {
            console.error("❌ [Tool - generateQuiz] Erreur:", error);
            throw error;
          }
        },
      },
      /*webSearch: {
        description:
          "Conducts Internet research to find current and relevant information or access to a specific website. You can do multiple searches one after the other to get more results and go more in depth of a subject. You can choose the number of results you want to get depending on the complexity of your request.",
        parameters: z.object({
          query: z.string().describe("The search query"),
          maxResults: z
            .number()
            .optional()
            .default(5)
            .describe(
              "Maximum number of results (default: 5). You can choose the number of results you want to get depending on the complexity of your request."
            ),
        }),
        execute: async ({ query, maxResults = 5 }) => {
          console.log(
            "🌐 [Tool - webSearch] Query:",
            query,
            "MaxResults:",
            maxResults
          );
          try {
            const webSearchUrl = new URL(
              "/api/web-search",
              process.env.NEXTAUTH_URL || "http://localhost:3000"
            );

            const response = await fetch(webSearchUrl.toString(), {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ query, maxResults }),
            });

            if (!response.ok) {
              throw new Error("Échec de la recherche web");
            }

            const results = await response.json();
            console.log(
              "✅ [Tool - webSearch] Résultats trouvés:",
              results.length
            );
            return {
              results: results.map(
                (result: { title: string; content: string; url: string }) => ({
                  title: result.title,
                  content: result.content,
                  url: result.url,
                })
              ),
              query,
            };
          } catch (error) {
            console.error("❌ [Tool - webSearch] Erreur:", error);
            throw error;
          }
        },
      },*/
    },
  });
  console.log(result);
  return result.toDataStreamResponse();
}

function shuffleArray(array: string[]) {
  return array.sort(() => Math.random() - 0.5);
}
