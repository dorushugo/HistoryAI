import { semanticSearch } from "@/lib/ragSearch";
import { openai } from "@ai-sdk/openai";
import { streamText, generateObject, Message } from "ai";
import { z } from "zod";

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai("gpt-4o"),
    system:
      "You are a helpful assistant that can answer questions about history. Answer only about the history of wars, nothing else. Politly decline to answer questions that are not about history of wars. You can use the searchWarsInfo tool to search into the database of HistoryAI for relevant information. When you have the answer, answer in the user's language in markdown format. IMPORTANT: When a quiz is generated, you must ONLY respond with 'Quiz généré !' without any additional explanation or recap. When a study card is generated, you must ONLY respond with 'Fiche de révision générée !' without any additional explanation or recap - the interface will handle the display of content.",
    messages,
    maxSteps: 5,
    experimental_toolCallStreaming: true,
    toolChoice: "auto",
    tools: {
      searchWarsInfo: {
        description:
          "Searches wars documents in the user's documents provided into HistoryAI for relevant information. You can do multiple searches one after the other to get more results and go more in depth of a subject. The database is in french so your queries should be in french too. Search by using the name of the war.",
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
          shouldRespondInText: z
            .boolean()
            .default(false)
            .describe("Indique si une réponse textuelle est nécessaire"),
        }),
        execute: async ({ question, lang }) => {
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
                        explanation: z
                          .string()
                          .describe(
                            "Explication détaillée de la réponse correcte"
                          ),
                      })
                    )
                    .min(3)
                    .max(10),
                }),
              }),
              system: `Expert en histoire militaire. Génère un quiz cohérent basé sur l'historique de conversation et les données vérifiées. 
                      Pour chaque question, fournis une explication détaillée qui aide à comprendre pourquoi la réponse est correcte.
                      Considère le contexte suivant: ${messages
                        .map((m: Message) => m.content)
                        .join("\n")}
                      Structure les questions avec 4 options, une réponse claire et une explication pédagogique.`,
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
                  options: shuffleArray(q.options),
                  correctIndex: q.options.indexOf(q.correctAnswer),
                  explanation: q.explanation,
                })),
              },
              message: "Quiz généré !",
            };
          } catch (error) {
            console.error("❌ [Tool - generateQuiz] Erreur:", error);
            throw error;
          }
        },
      },
      generateStudyCard: {
        description:
          "Génère une fiche de révision structurée sur un sujet historique lié aux guerres.",
        parameters: z.object({
          topic: z.string().describe("Sujet de la fiche de révision"),
          lang: z
            .string()
            .default("fr")
            .describe("Langue de sortie pour la fiche"),
        }),
        execute: async ({ topic, lang }) => {
          try {
            const { object: studyCardData } = await generateObject({
              model: openai("gpt-4o"),
              schema: z.object({
                studyCard: z.object({
                  title: z.string(),
                  introduction: z.string(),
                  keyPoints: z.array(
                    z.object({
                      title: z.string(),
                      content: z.string(),
                    })
                  ),
                  dates: z.array(
                    z.object({
                      date: z.string(),
                      event: z.string(),
                    })
                  ),
                  keyFigures: z.array(
                    z.object({
                      name: z.string(),
                      role: z.string(),
                      description: z.string(),
                    })
                  ),
                  conclusion: z.string(),
                }),
              }),
              system: `Expert en histoire militaire. Génère une fiche de révision structurée et détaillée.
                      La fiche doit inclure une introduction, des points clés, une chronologie, des personnages importants et une conclusion.
                      Sois précis et pédagogique dans tes explications.`,
              messages: [
                {
                  role: "user",
                  content: `Crée une fiche de révision sur: ${topic} (Langue: ${lang})`,
                },
              ],
            });

            return {
              studyCard: studyCardData.studyCard,
              message: "Fiche de révision générée !",
            };
          } catch (error) {
            console.error("❌ [Tool - generateStudyCard] Erreur:", error);
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
