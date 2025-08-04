import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use a headless backend
from matplotlib.backends.backend_pdf import PdfPages

import cv2
from pose.pose_estimator import PoseEstimator

def save_json_and_csv(results, video_id, output_dir="reports"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Save summary.json
    summary_path = os.path.join(output_dir, f"{video_id}_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(results["summary"], f, indent=2)
    
    # Save results.csv
    frame_data = pd.DataFrame(results["frame_data"])
    csv_path = os.path.join(output_dir, f"{video_id}_results.csv")
    frame_data.to_csv(csv_path, index=False)

    return summary_path, csv_path

def generate_pdf_report(video_id, results, frames, output_dir="reports"):
    pdf_path = os.path.join(output_dir, f"{video_id}.pdf")
    os.makedirs(output_dir, exist_ok=True)


    with PdfPages(pdf_path) as pdf:
        # Page 1: Summary
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        ax.set_title("Exercise Summary", fontsize=16, fontweight='bold')
        summary = results["summary"]

        text = ""
        for exercise in summary:
            block = summary[exercise]
            text += f"\n{exercise.upper()}:\n"
            text += f"  Total Reps: {block['total_reps']}\n"
            text += f"  Good Form Reps: {block['good_form_reps']}\n"
            issues = ', '.join(set(block['common_issues'])) or 'None'
            text += f"  Common Issues: {issues}\n"
        
        ax.text(0.05, 0.95, text, fontsize=12, va='top')
        pdf.savefig(fig)
        plt.close()

        # Page 2: Bar chart of good vs bad reps
        fig, ax = plt.subplots()
        for exercise in summary:
            good = summary[exercise]["good_form_reps"]
            total = summary[exercise]["total_reps"]
            bad = total - good
            ax.bar(exercise, good, label="Good", color='green')
            ax.bar(exercise, bad, bottom=good, label="Bad", color='red')
        ax.set_title("Good vs Bad Form Reps")
        ax.set_ylabel("Repetitions")
        pdf.savefig(fig)
        plt.close()

        # Page 3+: Angle plots per exercise
        df = pd.DataFrame(results["frame_data"])
        for exercise in df["exercise"].unique():
            sub = df[df["exercise"] == exercise]
            fig, ax = plt.subplots()
            ax.plot(sub["frame_index"], [d.get("knee") or d.get("elbow") for d in sub["angles"]])
            ax.set_title(f"{exercise.title()} Angle vs Frame")
            ax.set_xlabel("Frame Index")
            ax.set_ylabel("Angle (degrees)")
            pdf.savefig(fig)
            plt.close()

        # Annotated Sample Frames
        pose_estimator = PoseEstimator()
        for row in df.sample(n=min(4, len(df))).itertuples():
            idx = row.frame_index
            frame = frames[idx]
            landmarks = pose_estimator.extract_keypoints(frame)
            if landmarks:
                annotated = pose_estimator.draw_pose(frame.copy(), landmarks)
                fig, ax = plt.subplots()
                ax.imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
                ax.set_title(f"{row.exercise.title()} Frame {idx} - Rep {row.rep_id}")
                ax.axis('off')
                pdf.savefig(fig)
                plt.close()
    # Save the PDF
    print(f"Report saved to {pdf_path}")
    

    return pdf_path
