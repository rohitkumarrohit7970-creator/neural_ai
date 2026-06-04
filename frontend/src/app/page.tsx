"use client";

import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import { Search, Loader2, Database, AlertCircle, BarChart3, TrendingUp } from "lucide-react";

interface AnalysisResult {
  query: string;
  explanation: string;
  is_out_of_scope: boolean;
  chart_type: "bar" | "line" | "none";
  data?: any[];
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) throw new Error("Analysis failed");
      const data = await response.json();
      
      // For the prototype, we'll simulate the data result 
      // since the Python backend isn't integrated via API yet
      if (!data.is_out_of_scope && data.chart_type !== "none") {
        data.data = [
          { name: "Kerala", value: 45000 },
          { name: "Tamil Nadu", value: 65000 },
          { name: "Karnataka", value: 38000 },
          { name: "Maharashtra", value: 55000 },
          { name: "Gujarat", value: 32000 },
        ];
      }
      
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-slate-900 flex items-center justify-center gap-3">
            <Database className="w-10 h-10 text-blue-600" />
            Talk to Government Data
          </h1>
          <p className="text-slate-500 text-lg">
            Ask questions about Road Accidents in India (2019-2023) in plain English.
          </p>
        </div>

        {/* Search Input */}
        <div className="relative group">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
            placeholder="e.g., Which state had the most accidents in 2023?"
            className="w-full p-6 pr-16 text-lg rounded-2xl border-2 border-slate-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-50/50 outline-none transition-all shadow-sm group-hover:shadow-md"
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-slate-300 transition-colors"
          >
            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Search className="w-6 h-6" />}
          </button>
        </div>

        {/* Results Section */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-center gap-3">
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Analysis Card */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 space-y-4">
              <div className="flex items-center gap-2 text-blue-600 font-semibold uppercase tracking-wider text-sm">
                <TrendingUp className="w-4 h-4" />
                Analysis & Explanation
              </div>
              <p className="text-slate-700 text-lg leading-relaxed">
                {result.explanation}
              </p>
              
              {result.is_out_of_scope && (
                <div className="p-4 bg-amber-50 border border-amber-200 text-amber-800 rounded-lg text-sm italic">
                  Note: This request is considered out of the scope for the current dataset.
                </div>
              )}
            </div>

            {/* Visualization Card */}
            {!result.is_out_of_scope && result.chart_type !== "none" && (
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 space-y-4">
                <div className="flex items-center gap-2 text-purple-600 font-semibold uppercase tracking-wider text-sm">
                  <BarChart3 className="w-4 h-4" />
                  Visualization
                </div>
                <div className="h-[400px] w-full pt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    {result.chart_type === "bar" ? (
                      <BarChart data={result.data}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    ) : (
                      <LineChart data={result.data}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={3} dot={{ r: 6 }} />
                      </LineChart>
                    )}
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Audit Trail */}
            {!result.is_out_of_scope && (
              <div className="bg-slate-900 p-6 rounded-2xl shadow-lg space-y-4">
                <div className="flex items-center gap-2 text-slate-400 font-mono uppercase tracking-wider text-xs">
                  Audit Trail: Query Executed
                </div>
                <code className="block font-mono text-blue-400 overflow-x-auto whitespace-pre p-2 bg-slate-800/50 rounded">
                  {result.query}
                </code>
              </div>
            )}
          </div>
        )}

        {/* Example Queries */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-8">
          {[
            "Which state had the most accidents in 2023?",
            "Trend of accidents in Tamil Nadu from 2019-2023",
            "How many people died in road accidents in 2023?",
            "What was the wheat production in Punjab?",
          ].map((ex) => (
            <button
              key={ex}
              onClick={() => setQuestion(ex)}
              className="p-4 text-left text-slate-600 bg-white hover:bg-blue-50 hover:text-blue-600 border border-slate-200 rounded-xl transition-all text-sm font-medium"
            >
              "{ex}"
            </button>
          ))}
        </div>
      </div>
    </main>
  );
}
