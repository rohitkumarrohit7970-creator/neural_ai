import Groq from "groq-sdk";

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const client = new Groq({ apiKey: GROQ_API_KEY });

const DATASET_DESCRIPTION = `
Dataset: Road Accidents in India (State-wise, 2019-2023)
Columns: state, accidents_2019, accidents_2020, accidents_2021, accidents_2022, accidents_2023
Description: The values in 'accidents_YYYY' columns represent the total number of road accidents in that state for that year.
The dataset includes all major Indian states.
`;

export async function POST(req: Request) {
  if (!GROQ_API_KEY) {
    return Response.json({ error: "GROQ_API_KEY not configured" }, { status: 500 });
  }

  try {
    const { question } = await req.json();

    const prompt = `
      You are a data analyst. Based on the dataset schema below, write a Python snippet using 'df' to answer the question.
      
      Schema:
      ${DATASET_DESCRIPTION}
      
      Question: ${question}
      
      Constraint: Return ONLY a valid JSON object with:
      1. "query": The pandas code to execute (e.g., "df[df['state'] == 'Kerala']['accidents_2023'].values[0]")
      2. "explanation": What this query does in plain English.
      3. "is_out_of_scope": true if the question cannot be answered by this data, false otherwise.
      4. "chart_type": "bar", "line", or "none".
      
      Example JSON output:
      {
          "query": "df[df['accidents_2023'] == df['accidents_2023'].max()][['state', 'accidents_2023']]",
          "explanation": "Identifies the state with the highest number of accidents in 2023.",
          "is_out_of_scope": false,
          "chart_type": "none"
      }
    `;

    const completion = await client.chat.completions.create({
      messages: [
        { role: "system", content: "You are a helpful data analyst that outputs only JSON." },
        { role: "user", content: prompt }
      ],
      model: "llama-3.3-70b-versatile",
      response_format: { type: "json_object" }
    });

    const analysis = JSON.parse(completion.choices[0].message.content || "{}");

    // Since we are in a Next.js environment but the logic is designed for Python,
    // we would typically proxy this to a Python backend.
    // For this prototype, we'll return the analysis and the query.
    
    return Response.json(analysis);
  } catch (error: any) {
    return Response.json({ error: error.message }, { status: 500 });
  }
}
