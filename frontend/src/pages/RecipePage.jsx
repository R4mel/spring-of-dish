// src/pages/RecipePage.jsx
import React, { useState } from "react";
import styles from "./RecipePage.module.css";
import recipe from "../data/recipe.json"; // 경로 맞게 수정
import { saveRecipe } from "../api";       // ← 추가된 부분

export default function RecipePage() {
  // recipe.json에 id 필드가 있다고 가정
  const { id, title, subtitle, youtubeLink, ingredients, seasonings, steps } = recipe;

  // 유튜브 썸네일 url 생성
  const videoId = new URL(youtubeLink).searchParams.get("v");
  const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;

  // tts(이모지 토글)
  const [isPaused, setIsPaused] = useState(false);

  // 재생/일시정지 토글
  const handleTTS = () => {
    if (!window.speechSynthesis) {
      alert("TTS를 지원하지 않는 브라우저입니다.");
      return;
    }
    const synth = window.speechSynthesis;

    // 재생 중 & 일시정지 상태 아니면 → 일시정지
    if (synth.speaking && !synth.paused) {
      synth.pause();
      setIsPaused(true);
      return;
    }
    // 일시정지 상태면 → 재개
    if (synth.paused) {
      synth.resume();
      setIsPaused(false);
      return;
    }

    // 새로 재생
    synth.cancel(); // 큐 초기화
    const textToRead = steps.join(". ");
    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.lang = "ko-KR";
    utterance.onstart = () => setIsPaused(false);
    utterance.onend   = () => setIsPaused(false);
    synth.speak(utterance);
  };

  // — 3) 저장 핸들러 추가
  const handleSave = async () => {
    try {
      await saveRecipe(id);
      alert("⭐ 레시피가 저장되었습니다!");
    } catch (err) {
      console.error(err);
      alert("저장에 실패했습니다.");
    }
  };

  return (
    <div className={styles.pageContainer}>
      <div className={styles.categoryWrapper}>
        {/* 썸네일 */}
        <img
          src={thumbnailUrl}
          alt="레시피 썸네일"
          className={styles.thumbnail}
        />

        {/* 콘텐츠 */}
        <div className={styles.content}>
          {/* tts, 즐겨찾기 버튼 */}
          <div className={styles.topIcons}>
            <button onClick={handleTTS} className={styles.iconButton}>
              {/* 일시정지 중이면 ▶, 아니면 🦻 */}
              {isPaused ? "▶" : "🦻"}
            </button>
            {/* 4) 별 버튼에 onClick 연결 */}
            <button onClick={handleSave} className={styles.iconButton}>
              ⭐
            </button>
          </div>

          <h1 className={styles.title}>{title}</h1>
          <p className={styles.subtitle}>{subtitle}</p>

          <h2 className={styles.sectionTitle}>식재료</h2>
          <div className={styles.ingredientList}>
            {ingredients.map((item) => (
              <div key={item.name} className={styles.ingredientItem}>
                <img
                  src={item.iconUrl}
                  alt={item.name}
                  className={styles.ingredientIcon}
                />
                <div>{item.name}</div>
              </div>
            ))}
          </div>

          <h2 className={styles.sectionTitle}>조미료</h2>
          <div className={styles.ingredientList}>
            {seasonings.map((item) => (
              <div key={item.name} className={styles.ingredientItem}>
                <img
                  src={item.iconUrl}
                  alt={item.name}
                  className={styles.ingredientIcon}
                />
                <div>{item.name}</div>
              </div>
            ))}
          </div>

          <h2 className={styles.sectionTitle}>레시피</h2>
          <ol className={styles.recipeSteps}>
            {steps.map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>

          <div className={styles.youtubeLink}>
            <a href={youtubeLink} target="_blank" rel="noopener noreferrer">
              ▶ 유튜브로 보기
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
