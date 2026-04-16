import React, { useState } from "react";
import StudentView from "./StudentView";
import FloaterView from "./FloaterView";

export default function App() {
  const [view, setView] = useState("student");

  return (
    <div>
      <div style={{ padding: "1rem", display: "flex", gap: "1rem" }}>
        <button onClick={() => setView("student")}>Student View</button>
        <button onClick={() => setView("floater")}>Floater View</button>
      </div>

      {view === "student" ? <StudentView /> : <FloaterView />}
    </div>
  );
}