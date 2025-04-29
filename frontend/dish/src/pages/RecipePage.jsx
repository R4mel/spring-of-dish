import React from "react";
import styles from "./RecipePage.module.css";
import recipe from "../data/recipe.json";  // 경로 맞게 수정

export default function RecipePage() {
  const { title, subtitle, youtubeLink, ingredients, seasonings, steps } = recipe;

  const videoId = new URL(youtubeLink).searchParams.get("v");
  const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;

  const handleTTS = () => {
    if (!window.speechSynthesis) {
      alert("TTS를 지원하지 않는 브라우저입니다.");
      return;
    }
    const textToRead = steps.join(". ");
    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.lang = "ko-KR";
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
  };

  return (
    <div className={styles.pageContainer}>
      {/* 썸네일 */}
      <img src={thumbnailUrl} alt="레시피 썸네일" className={styles.thumbnail} />

      {/* 콘텐츠 */}
      <div className={styles.content}>
        {/* TTS, 즐겨찾기 버튼 */}
        <div className={styles.topIcons}>
          <button onClick={handleTTS} className={styles.iconButton}>🦻</button>
          <button className={styles.iconButton}>⭐</button>
        </div>

        <h1 className={styles.title}>{title}</h1>
        <p className={styles.subtitle}>{subtitle}</p>

        {/* 식재료 */}
        <h2 className={styles.sectionTitle}>식재료</h2>
        <div className={styles.ingredientList}>
          {ingredients.map((item) => (
            <div key={item.name} className={styles.ingredientItem}>
              <img src={item.iconUrl} alt={item.name} className={styles.ingredientIcon} />
              <div>{item.name}</div>
            </div>
          ))}
        </div>

        {/* 조미료 */}
        <h2 className={styles.sectionTitle}>조미료</h2>
        <div className={styles.ingredientList}>
          {seasonings.map((item) => (
            <div key={item.name} className={styles.ingredientItem}>
              <img src={item.iconUrl} alt={item.name} className={styles.ingredientIcon} />
              <div>{item.name}</div>
            </div>
          ))}
        </div>

        {/* 레시피 절차 */}
        <h2 className={styles.sectionTitle}>레시피</h2>
        <ol className={styles.recipeSteps}>
          {steps.map((step, idx) => (
            <li key={idx}>{step}</li>
          ))}
        </ol>

        {/* 유튜브 링크 */}
        <div className={styles.youtubeLink}>
          <a href={youtubeLink} target="_blank" rel="noopener noreferrer">▶ 유튜브로 보기</a>
        </div>
      </div>
    </div>
  );
}