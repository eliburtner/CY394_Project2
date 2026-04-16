import React, { useEffect, useState } from "react";

const API_BASE_URL = "http://localhost:5000";

export default function FloaterView() {
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const fetchTables = async () => {
    try {
      setError("");
      const response = await fetch(`${API_BASE_URL}/tables`);

      if (!response.ok) {
        throw new Error("Failed to fetch tables");
      }

      const data = await response.json();
      setTables(data);
    } catch (err) {
      setError(err.message || "Something went wrong while loading tables.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchTables();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchTables();
  };

  if (loading) {
    return <div style={styles.page}>Loading available tables...</div>;
  }

  return (
    <div style={styles.page}>
      <div style={styles.headerRow}>
        <h1 style={styles.heading}>Available Tables</h1>
        <button onClick={handleRefresh} style={styles.refreshButton}>
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <p style={styles.subtext}>
        Students without seats can view current table availability below.
      </p>

      {error && <div style={styles.error}>{error}</div>}

      {tables.length === 0 ? (
        <div style={styles.emptyState}>No tables found.</div>
      ) : (
        <div style={styles.grid}>
          {tables.map((table) => (
            <div key={table.id || table.table_id} style={styles.card}>
              <h2 style={styles.cardTitle}>
                Table {table.table_id ?? table.id}
              </h2>

              <p style={styles.cardText}>
                <strong>Available Seats:</strong>{" "}
                {table.available_seats ?? 0}
              </p>

              <p style={styles.cardText}>
                <strong>Status:</strong>{" "}
                {(table.available_seats ?? 0) > 0 ? "Open" : "Full"}
              </p>

              <button
                style={{
                  ...styles.claimButton,
                  opacity: (table.available_seats ?? 0) > 0 ? 1 : 0.6,
                  cursor:
                    (table.available_seats ?? 0) > 0 ? "pointer" : "not-allowed",
                }}
                disabled={(table.available_seats ?? 0) <= 0}
                onClick={() =>
                  alert(
                    "Reserve-seat functionality can be connected here once your backend route is ready."
                  )
                }
              >
                Claim Seat
              </button>
            </div>
          ))}
        </div>
      )}
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
  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "1rem",
  },
  heading: {
    margin: 0,
  },
  subtext: {
    color: "#555",
    marginBottom: "1.5rem",
  },
  refreshButton: {
    padding: "0.6rem 1rem",
    border: "none",
    borderRadius: "8px",
    backgroundColor: "#2563eb",
    color: "white",
    cursor: "pointer",
  },
  error: {
    backgroundColor: "#fee2e2",
    color: "#991b1b",
    padding: "0.75rem",
    borderRadius: "8px",
    marginBottom: "1rem",
  },
  emptyState: {
    backgroundColor: "white",
    padding: "1rem",
    borderRadius: "10px",
    textAlign: "center",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
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
    marginBottom: "0.75rem",
  },
  cardText: {
    margin: "0.5rem 0",
  },
  claimButton: {
    marginTop: "1rem",
    width: "100%",
    padding: "0.75rem",
    border: "none",
    borderRadius: "8px",
    backgroundColor: "#16a34a",
    color: "white",
    fontWeight: "bold",
  },
};