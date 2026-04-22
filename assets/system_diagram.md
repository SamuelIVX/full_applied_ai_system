# VibeFinder 2.0 — System Architecture

```mermaid
flowchart TD
    subgraph INPUT["User Input Layer"]
        A1([Natural Language\n"upbeat pop music"]) --> A2
        A3([Quick Start Button\n☀️ Morning Run]) --> A2
        A4([Manual Sliders\nSidebar Override]) --> A2
    end

    subgraph CORE["Core Processing Layer"]
        A2[NL Parser] --> B[Extract Preferences\ngenre · mood · energy\nvalence · acousticness]
        
        B --> C[Conversation State Manager]
        C --> C1{Confidence ≥ 0.6?}
        C1 -->|No| C2[Clarification Agent\nAsk follow-up question]
        C2 --> A2
        C1 -->|Yes| D[Recommender Engine]
        
        E[Genre Similarity Lookup] -.->|partial credit| D
    end

    subgraph STORAGE["Data Layer"]
        F[(songs.csv\n20 songs)] --> D
        G[(.vibefinder_state.json\nSession Persistence)] -.-> C
    end

    subgraph EVAL["Evaluation Layer"]
        D --> H[Score Songs\nweighted algorithm]
        H --> I[Edge Case Detector]
        I --> I1{Issues Found?}
        I1 -->|Yes| I2[Generate Warnings]
        I1 -->|No| J[Rank & Sort Results]
        I2 --> J
        J --> K[top-k recommendations]
    end

    subgraph OUTPUT["User Interface"]
        K --> L[Streamlit UI\nChat History + Results]
        L --> L1[Score Display\ncolor-coded]
        L --> L2[Expand Details\n"Why this?"]
        L --> L3[Warnings Panel\nEdge cases]
    end

    subgraph TESTING["Verification Layer"]
        T1[Unit Tests\npytest] -.->|verifies| B
        T2[Integration Tests\npytest] -.->|verifies| D
        T3[Manual Testing\nStreamlit UI] -.->|validates| L
    end

    style INPUT fill:#3498db,color:#fff
    style CORE fill:#9b59b6,color:#fff
    style STORAGE fill:#e74c3c,color:#fff
    style EVAL fill:#f39c12,color:#fff
    style OUTPUT fill:#27ae60,color:#fff
    style TESTING fill:#1abc9c,color:#fff
```

## Component Description

| Component | File | Function |
|---|---|---|
| **NL Parser** | `src/nl_parser.py` | Rule-based keyword matching to extract structured preferences from free text |
| **Conversation State** | `src/state.py` | Tracks history, profile, confidence; triggers clarification questions |
| **Genre Similarity** | `src/genre_similarity.py` | Provides partial credit (0.0–1.0) for near-genre matches |
| **Recommender** | `src/recommender.py` | Scores songs using weighted algorithm (genre 0.20, mood 0.30, energy 0.30, valence 0.15, acousticness 0.05) |
| **Edge Case Detector** | `src/app.py` | Warns about unknown genres, extreme values, conflicting preferences |

## Data Flow

```
1. User Input → NL Parser → Structured Preferences
2. Preferences → Conversation State → Update Profile + Confidence
3. Confidence Check → [Low?] → Clarification Loop OR Continue
4. Profile → Recommender → Score All Songs
5. Scores → Edge Case Detector → Warnings (if any)
6. Sorted Results → Streamlit UI → Display
```

## Human/Testing Involvement

| Stage | Human/Test | Purpose |
|---|---|---|
| **Input Validation** | NL Parser Tests | Verify keyword mapping accuracy |
| **Profile Confidence** | Unit Test | Verify confidence scoring algorithm |
| **Recommendation Quality** | test_recommender.py | Verify backward compatibility |
| **End-to-End** | Manual Testing | User validates via Streamlit UI |
| **Edge Cases** | Warnings Displayed | Human reviews warnings |

## Confidence Scoring Algorithm

```
confidence = (specified_attributes / 5)
           + 0.1 if genre exists in catalog
           - 0.1 if genre unknown
           + 0.05 if mood recognized
           
threshold ≥ 0.6 → proceed to recommend
threshold < 0.6 → ask clarification
```

## Test Files

| Test File | Coverage |
|---|---|
| `tests/test_nl_parser.py` | 20 tests for NL preference extraction |
| `tests/test_recommender.py` | 2 tests for ranking and explanation |