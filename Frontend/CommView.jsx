import React, { useEffect, useState } from "react";

const API_BASE_URL = "http://localhost:5000";

export default function CommView() {
  const [tables, setTables] = useState([]);
  const [seatInputs, setSeatInputs] = useState({});
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const fetchTables = async () => {
    try {
      setError("");
      const response = await fetch(`${API_BASE_URL}/tables`);

      if (!response.ok) {
        throw new Error("Failed to fetch tables");
      }

      const data = await response.json();
      setTables(data);

      const initialInputs = {};
      data.forEach((table) => {
        initialInputs[table.table_id ?? table.id] =
          table.available_seats ?? 0;
      });
      setSeatInputs(initialInputs);
    } catch (err) {
      setError(err.message || "Could not load table data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTables();
  }, []);

  const handleInputChange = (tableId, value) => {
    setSeatInputs((prev) => ({
      ...prev,
      [tableId]: value,
    }));
  };

  const handleUpdate = async (tableId) => {
    try {
      setMessage("");
      setError("");

      const availableSeats = Number(seatInputs[tableId]);

      if (Number.isNaN(availableSeats) || availableSeats < 0) {
        setError("Available seats must be a non-negative number.");
        return;
      }

      const response = await fetch(`${API_BASE_URL}/update-seats`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          table_id: tableId,
          user_id: 1,
          available_seats: availableSeats,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to update seats.");
      }

      setMessage(`Table ${tableId} updated successfully.`);
      fetchTables();
    } catch (err) {
      setError(err.message || "Something went wrong while updating seats.");
    }
  };

  if (loading) {
    return <div style={styles.page}>Loading Table Commadant dashboard...</div>;
  }

  return (
    <div style={styles.page}>
      <h1 style={styles.heading}>Table Commadant Dashboard</h1>
      <p style={styles.subtext}>
        Update available seats for each table below.
      </p>

      {message && <div style={styles.success}>{message}</div>}
      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.tableList}>
        {tables.map((table) => {
          const tableId = table.table_id ?? table.id;
          const currentSeats = table.available_seats ?? 0;

          return (
            <div key={tableId} style={styles.card}>
              <h2 style={styles.cardTitle}>Table {tableId}</h2>

              <p style={styles.cardText}>
                <strong>Current Available Seats:</strong> {currentSeats}
              </p>

              <label style={styles.label}>
                New Available Seat Count:
                <input
                  type="number"
                  min="0"
                  value={seatInputs[tableId] ?? ""}
                  onChange={(e) =>
                    handleInputChange(tableId, e.target.value)
                  }
                  style={styles.input}
                />
              </label>

              <div style={styles.buttonRow}>
                <button
                  style={styles.smallButton}
                  onClick={() =>
                    handleInputChange(
                      tableId,
                      Math.max(0, Number(seatInputs[tableId] || 0) - 1)
                    )
                  }
                >
                  -1
                </button>

                <button
                  style={styles.smallButton}
                  onClick={() =>
                    handleInputChange(
                      tableId,
                      Number(seatInputs[tableId] || 0) + 1
                    )
                  }
                >
                  +1
                </button>

                <button
                  style={styles.updateButton}
                  onClick={() => handleUpdate(tableId)}
                >
                  Update
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const styles = {
  page: {
    padding: "2rem",
    fontFamily: "Arial, sans-serif",
    backgroundColor: "#f7f9fc",
    minHeight: "100vh",
  },
  heading: {
    marginBottom: "0.5rem",
  },
  subtext: {
    color: "#555",
    marginBottom: "1.5rem",
  },
  success: {
    backgroundColor: "#dcfce7",
    color: "#166534",
    padding: "0.75rem",
    borderRadius: "8px",
    marginBottom: "1rem",
  },
  error: {
    backgroundColor: "#fee2e2",
    color: "#991b1b",
    padding: "0.75rem",
    borderRadius: "8px",
    marginBottom: "1rem",
  },
  tableList: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "1rem",
  },
  card: {
    backgroundColor: "white",
    padding: "1.25rem",
    borderRadius: "12px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
  },
  cardTitle: {
    marginTop: 0,
  },
  cardText: {
    marginBottom: "1rem",
  },
  label: {
    display: "block",
    marginBottom: "1rem",
    fontWeight: "bold",
  },
  input: {
    display: "block",
    width: "100%",
    marginTop: "0.5rem",
    padding: "0.6rem",
    borderRadius: "8px",
    border: "1px solid #ccc",
    boxSizing: "border-box",
  },
  buttonRow: {
    display: "flex",
    gap: "0.5rem",
    flexWrap: "wrap",
  },
  smallButton: {
    padding: "0.65rem 0.9rem",
    border: "none",
    borderRadius: "8px",
    backgroundColor: "#dbeafe",
    cursor: "pointer",
  },
  updateButton: {
    padding: "0.65rem 1rem",
    border: "none",
    borderRadius: "8px",
    backgroundColor: "#2563eb",
    color: "white",
    cursor: "pointer",
    fontWeight: "bold",
  },
};
