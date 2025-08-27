import React, { useState, useEffect } from "react";

const CELL_SIZE = 40; // pixels

const BACKEND_BASE = `${window.location.hostname}:8000`;

export default function GridBoard() {
  // In reality you'll fetch these from backend
  const [gridSize, setGridSize] = useState({ width: 14, height: 14 });
  const [obj, setObj] = useState(null);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const socket = new WebSocket(`ws://${BACKEND_BASE}/ws_test`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // print the data
      console.log(data);

      if (data.type === "init" || data.type === "update") {
        setObj(data.location);
      }
    };

    setWs(socket);

    return () => {
      socket.close();
    };
  }, []);

  const moveCircle = (x, y) => {
    if (ws) {
      ws.send(JSON.stringify({ type: "move", x, y }));
    }
  };

  return (
    <div
      className="grid"
      style={{
        display: "grid",
        gridTemplateRows: `repeat(${gridSize.height}, ${CELL_SIZE}px)`,
        gridTemplateColumns: `repeat(${gridSize.width}, ${CELL_SIZE}px)`,
        border: "2px solid black",
        width: `${gridSize.width * CELL_SIZE}px`,
        height: `${gridSize.height * CELL_SIZE}px`,
        position: "relative",
      }}
    >
        {/* Render grid cells with borders */}
        {Array.from({ length: gridSize.width * gridSize.height }).map((_, idx) => {
          const x = idx % gridSize.width;
          const y = Math.floor(idx / gridSize.width);
          return (
            <div
              key={`cell-${x}-${y}`}
              style={{
                border: "1px solid #ccc",
                width: `${CELL_SIZE}px`,
                height: `${CELL_SIZE}px`,
                boxSizing: "border-box",
                gridRowStart: y + 1,
                gridColumnStart: x + 1,
                cursor: "pointer",
              }}
              onClick={() => moveCircle( x, y )}
            />
          );
        })}
      {/* Circle: only show after first click */}
      {obj && (
        <div
          style={{
            gridRowStart: obj.y + 1, // grid is 1-based
            gridColumnStart: obj.x + 1,
            justifySelf: "center",
            alignSelf: "center",
            width: `${CELL_SIZE / 2}px`,
            height: `${CELL_SIZE / 2}px`,
            borderRadius: "50%",
            backgroundColor: "red",
          }}
        />
      )}
    </div>
  );
}
