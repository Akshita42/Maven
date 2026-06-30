const API_BASE = "http://127.0.0.1:8000/api/v1";

export class MavenAPI {
  static async resolveCompany(query: string) {
    const res = await fetch(`${API_BASE}/company/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ company: query })
    });
    const data = await res.json();
    if (!res.ok || data.status === "error") throw new Error(data.error?.message || "Failed to resolve company");
    return data.data;
  }

  static async chatStream(
    query: string,
    sessionId: string,
    reportId: string | null,
    history: any[],
    currentCompany: string | null,
    explainabilityLevel: string,
    callbacks: {
      onStage?: (stage: string, status: string, message?: string) => void;
      onEvidence?: (data: any) => void;
      onCommittee?: (data: any) => void;
      onRecommendation?: (data: any) => void;
      onCompleted?: (reportId: string, data: any, content?: string) => void;
      onError?: (stage: string, error: string) => void;
    }
  ) {
    const payload = {
      query,
      sessionId,
      reportId,
      history,
      currentCompany,
      explainabilityLevel
    };

    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Failed to reach Maven backend (${response.status})`);
      }

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Parse SSE chunks
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || ""; // Keep the incomplete line in the buffer

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "");
            try {
              const event = JSON.parse(dataStr);
              switch (event.type) {
                case "stage":
                  if (callbacks.onStage) callbacks.onStage(event.stage, event.status, event.message);
                  break;
                case "evidence":
                  if (callbacks.onEvidence) callbacks.onEvidence(event.data);
                  break;
                case "committee":
                  if (callbacks.onCommittee) callbacks.onCommittee(event.data);
                  break;
                case "recommendation":
                  if (callbacks.onRecommendation) callbacks.onRecommendation(event.data);
                  break;
                case "completed":
                  if (callbacks.onCompleted) callbacks.onCompleted(event.reportId, event.data, event.content);
                  break;
                case "error":
                  if (callbacks.onError) callbacks.onError(event.stage, event.error);
                  break;
              }
            } catch (e) {
              console.error("Error parsing SSE event:", e, dataStr);
            }
          }
        }
      }
    } catch (err: any) {
      if (callbacks.onError) callbacks.onError("network", err.message || "Failed to connect to Maven.");
    }
  }

  static async challengeRecommendation(reportId: string) {
    throw new Error("Challenge endpoint not ready yet.");
  }

  static async explainRecommendation(reportId: string, level: string) {
    throw new Error("Explain endpoint not ready yet.");
  }
}
