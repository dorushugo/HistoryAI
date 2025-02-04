"use client";

import { useChat } from "ai/react";
import { Send, BookOpen } from "lucide-react";
import { useRef, useEffect, useState } from "react";
import { Markdown } from "./components/markdown";
import cx from "classnames";
import { motion } from "framer-motion";
import type { Message, ToolInvocation } from "ai";

interface QuizData {
  title: string;
  questions: {
    question: string;
    options: string[];
    correctIndex: number;
    explanation?: string;
  }[];
}

const QuizComponent = ({ quiz }: { quiz: QuizData }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [score, setScore] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);

  const handleAnswer = (index: number) => {
    setSelectedAnswer(index);
    if (index === quiz.questions[currentQuestion].correctIndex) {
      setScore(score + 1);
    }
    setShowExplanation(true);
  };

  const nextQuestion = () => {
    setCurrentQuestion((prev) => prev + 1);
    setSelectedAnswer(null);
    setShowExplanation(false);
  };

  const progress = (currentQuestion / quiz.questions.length) * 100;

  return (
    <motion.div
      className="mt-4 p-6 bg-white rounded-xl shadow-lg border border-gray-100"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Barre de progression */}
      <div className="h-2 bg-gray-100 rounded-full mb-6">
        <div
          className="h-full bg-blue-500 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      <h3 className="text-xl font-bold text-gray-800 mb-2">{quiz.title}</h3>

      {currentQuestion < quiz.questions.length ? (
        <div>
          <motion.div
            key={currentQuestion}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <p className="text-lg font-medium text-gray-700 mb-6">
              {quiz.questions[currentQuestion].question}
            </p>

            <div className="grid gap-3">
              {quiz.questions[currentQuestion].options.map((option, index) => {
                const isCorrect =
                  index === quiz.questions[currentQuestion].correctIndex;
                const isSelected = selectedAnswer === index;

                return (
                  <motion.button
                    key={index}
                    onClick={() => !selectedAnswer && handleAnswer(index)}
                    className={cx(
                      "p-4 text-left rounded-xl border transition-all",
                      "flex items-center gap-3",
                      selectedAnswer !== null
                        ? isCorrect
                          ? "bg-green-50 border-green-500"
                          : isSelected
                          ? "bg-red-50 border-red-500"
                          : "border-gray-200"
                        : "hover:bg-gray-50 border-gray-200"
                    )}
                    disabled={selectedAnswer !== null}
                    whileHover={!selectedAnswer ? { scale: 1.02 } : undefined}
                  >
                    <div
                      className={cx(
                        "w-6 h-6 rounded-full flex items-center justify-center",
                        selectedAnswer !== null
                          ? isCorrect
                            ? "bg-green-500 text-white"
                            : isSelected
                            ? "bg-red-500 text-white"
                            : "bg-gray-200"
                          : "bg-gray-200"
                      )}
                    >
                      {String.fromCharCode(65 + index)}
                    </div>
                    <span className="flex-1">{option}</span>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>

          {showExplanation && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200"
            >
              <div className="flex items-start gap-3">
                <span className="text-blue-500">💡</span>
                <div>
                  <p className="font-medium text-blue-800 mb-2">
                    {selectedAnswer ===
                    quiz.questions[currentQuestion].correctIndex
                      ? "Bonne réponse !"
                      : "Explication"}
                  </p>
                  <p className="text-blue-700">
                    {quiz.questions[currentQuestion].explanation ||
                      "La réponse correcte est l'option " +
                        String.fromCharCode(
                          65 + quiz.questions[currentQuestion].correctIndex
                        )}
                  </p>
                </div>
              </div>

              <button
                onClick={nextQuestion}
                className="mt-4 bg-blue-600 text-white px-5 py-2.5 rounded-lg hover:bg-blue-700 
                         transition-colors flex items-center gap-2 ml-auto"
              >
                {currentQuestion < quiz.questions.length - 1
                  ? "Question suivante →"
                  : "Voir les résultats"}
              </button>
            </motion.div>
          )}
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="text-4xl mb-4">🎉</div>
          <p className="text-2xl font-bold text-gray-800 mb-4">
            Quiz terminé !
          </p>
          <p className="text-lg text-gray-600 mb-6">
            Votre score : {score}/{quiz.questions.length}
          </p>
          <button
            onClick={() => {
              setCurrentQuestion(0);
              setScore(0);
              setSelectedAnswer(null);
              setShowExplanation(false);
            }}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 
                     transition-colors font-medium"
          >
            Recommencer le quiz
          </button>
        </motion.div>
      )}
    </motion.div>
  );
};

export default function Home() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } =
    useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const renderToolInvocation = (toolInvocation: ToolInvocation) => {
    const { toolName, toolCallId, state } = toolInvocation;

    if (state !== "result") {
      return (
        <div
          key={toolCallId}
          className="flex items-center gap-2 text-gray-600 mt-2"
        >
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent" />
          <span>Recherche en cours...</span>
        </div>
      );
    }

    if (state === "result" && "result" in toolInvocation) {
      if (toolName === "generateQuiz") {
        const quizData = toolInvocation.result?.quiz;
        return quizData ? (
          <QuizComponent key={toolCallId} quiz={quizData} />
        ) : null;
      }

      const results = Array.isArray(toolInvocation.result)
        ? toolInvocation.result
        : [toolInvocation.result];

      return (
        <div key={toolCallId} className="mt-4 flex flex-wrap gap-2">
          {results.map((result, index) => {
            const match = result.match(/# (.*?)\n/);
            const title = match ? match[1] : "Article Wikipédia";
            const urlMatch = result.match(/\[.*?\]\((.*?)\)/);
            const url = urlMatch ? urlMatch[1] : "#";

            return (
              <a
                key={index}
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 p-2 bg-white rounded-lg border hover:bg-gray-50 transition-colors"
              >
                <BookOpen className="w-5 h-5 text-gray-600" />
                <span className="text-sm font-medium">{title}</span>
              </a>
            );
          })}
        </div>
      );
    }

    return null;
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="flex items-center justify-center p-4 border-b bg-white">
        <h1 className="text-xl font-bold text-gray-800">
          HistoryAI - Votre Guide Historique
        </h1>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message: Message) => (
          <motion.div
            key={message.id}
            initial={{ y: 5, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className={cx(
              "flex",
              message.role === "user" ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={cx(
                "max-w-[80%] rounded-lg p-4",
                message.role === "user"
                  ? "bg-blue-500 text-white rounded-br-none"
                  : "bg-white text-gray-800 rounded-bl-none border"
              )}
            >
              <div className="prose prose-sm max-w-none">
                <Markdown>{message.content}</Markdown>
              </div>

              {message.toolInvocations?.map(renderToolInvocation)}
            </div>
          </motion.div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-4 border-t bg-white">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            placeholder="Posez votre question sur l'histoire..."
            className="flex-1 p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}
