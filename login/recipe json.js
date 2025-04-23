import React from "react";
import recipe from "./recipe.json";

export default function RecipePage() {
  const { title, subtitle, youtubeLink, ingredients, seasonings, steps } =
    recipe;

  const videoId = new URL(youtubeLink).searchParams.get("v");
  const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;

  //재료아이콘, 이미지 경로수정 필요
  const circleStyle = {
    width: 50,
    height: 50,
    borderRadius: "50%",
    backgroundColor: "#ddd",
    margin: "0 auto",
  };

  //상단 tts, 즐겨찾기 더미 버튼튼
  const iconButtonStyle = {
    width: 32,
    height: 32,
    borderRadius: "50%",
    cursor: "pointer",
  };

  //tts기능
  const handleTTS = () => {
    if (!window.speechSynthesis) {
      alert("tts를 지원하지 않는 브라우저입니다다.");
      return;
    }
    const textToRead = steps.join(". ");
    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.lang = "ko-KR";
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
  };

  return (
    <div
      style={{
        width: "390px",
        height: "844px",
        margin: "0 auto",
        overflowY: "auto",
        padding: 0,
        boxSizing: "border-box",
      }}
    >
      {/* 유튜브 썸네일 */}
      <img
        src={thumbnailUrl}
        alt="레시피 썸네일"
        style={{
          width: "100%",
          height: 200,
          objectFit: "cover",
          borderRadius: 8,
        }}
      />

      {/* 메인 콘텐츠영역역 */}
      <div
        style={{
          position: "relative",
          backgroundColor: "#fff",
          padding: 16,
          marginTop: 0,
          boxSizing: "border-box",
        }}
      >
        {/* 우측 상단 아이콘위치 */}
        <div
          style={{
            position: "absolute",
            top: 16,
            right: 16,
            display: "flex",
            gap: 8,
          }}
        >
          <div
            onClick={handleTTS}
            style={{ ...iconButtonStyle, backgroundColor: "orange" }}
            title="레시피 읽어주기"
          />
          <div
            style={{ ...iconButtonStyle, backgroundColor: "yellow" }}
            title="즐겨찾기"
          />
        </div>

        {/* 제목, 부제 */}
        <h1 style={{ margin: 0 }}>{title}</h1>
        <p style={{ color: "#666", marginTop: 8 }}>{subtitle}</p>

        {/* 식재료 */}
        <h2 style={{ color: "#64C826", marginTop: 16 }}>식재료</h2>
        <div style={{ display: "flex", gap: 12 }}>
          {ingredients.map((i) => (
            <div key={i.name} style={{ textAlign: "center" }}>
              <div style={circleStyle} />
              <div>{i.name}</div>
            </div>
          ))}
        </div>

        {/* 조미료 */}
        <h2 style={{ color: "#64C826", marginTop: 16 }}>조미료</h2>
        <div style={{ display: "flex", gap: 12 }}>
          {seasonings.map((s) => (
            <div key={s.name} style={{ textAlign: "center" }}>
              <div style={circleStyle} />
              <div>{s.name}</div>
            </div>
          ))}
        </div>

        {/* 레시피 */}
        <h2 style={{ marginTop: 16 }}>레시피</h2>
        <ol style={{ paddingLeft: 16, marginTop: 8 }}>
          {steps.map((st, idx) => (
            <li key={idx} style={{ marginBottom: 8 }}>
              {st}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
