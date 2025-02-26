import React, { useState, useEffect } from 'react';
import { uploadImage, getSimilarMedicines } from './services/api';
import styles from './PrescriptionUpload.module.css'; // Use CSS Modules for styling

function PrescriptionUpload() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [results, setResults] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [similarMedicines, setSimilarMedicines] = useState({});
  const [loadingSimilar, setLoadingSimilar] = useState({});

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    setUploadedFile(file);

    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleUpload = async () => {
    if (!uploadedFile) return;
    try {
      setIsLoading(true);
      setSimilarMedicines({});
      setLoadingSimilar({});
      const data = await uploadImage(uploadedFile);
      setResults(data);
    } catch (error) {
      setResults({ error: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetSimilar = async (medicineName, index) => {
    try {
      setLoadingSimilar((prev) => ({ ...prev, [index]: true }));
      const similar = await getSimilarMedicines(medicineName);
      setSimilarMedicines((prev) => ({ ...prev, [index]: similar }));
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingSimilar((prev) => ({ ...prev, [index]: false }));
    }
  };

  const clearSelection = () => {
    setUploadedFile(null);
    setPreviewUrl(null);
    setResults(null);
    setSimilarMedicines({});
    setLoadingSimilar({});
  };

  const removeMedicine = (index) => {
    setResults((prev) => ({
      ...prev,
      Prescription: prev.Prescription.filter((_, i) => i !== index),
    }));
    setSimilarMedicines((prev) => {
      const updated = { ...prev };
      delete updated[index];
      return updated;
    });
  };

  const addMedicine = () => {
    // Example: Add a new medicine (you can customize this logic)
    const newMedicine = ['New Medicine', 'Description', 'Dosage', { status: 'not found' }];
    setResults((prev) => ({
      ...prev,
      Prescription: [...prev.Prescription, newMedicine],
    }));
  };

  return (
    <div className={styles.container}>
      <div className={styles.uploadSection}>
        <h2>Upload Prescription</h2>
        {!uploadedFile ? (
          <div className={styles.fileInputWrapper}>
            <input
              type="file"
              onChange={handleFileUpload}
              accept=".jpg,.png"
              title=" "
            />
            <p>Drag & drop or click to upload</p>
          </div>
        ) : (
          <>
            <div className={styles.previewContainer}>
              <img src={previewUrl} alt="Preview" className={styles.previewImage} />
              <button className={styles.clearButton} onClick={clearSelection}>
                ✕
              </button>
            </div>
            <p>Selected file: {uploadedFile.name}</p>
            <button className={styles.uploadButton} onClick={handleUpload}>
              {isLoading ? 'Uploading...' : 'Upload'}
            </button>
          </>
        )}
      </div>

      <div className={styles.resultsSection}>
        <h2>Results</h2>
        {isLoading ? (
          <div className={styles.loadingContainer}>
            <div className={styles.loadingSpinner}></div>
            <p>Processing image...</p>
          </div>
        ) : results ? (
          <div className={styles.resultsContent}>
            <button className={styles.addButton} onClick={addMedicine}>
              Add Medicine
            </button>
            {results.Prescription.map((item, index) => (
              <div key={index} className={styles.prescriptionCard}>
                <div className={styles.prescriptionDetails}>
                  <span className={styles.medicineName}>{item[0]}</span>
                  <span className={styles.description}>{item[1]}</span>
                  <span className={styles.dosage}>{item[2]}</span>
                  <button
                    className={`${styles.similarButton} ${
                      loadingSimilar[index] ? styles.loading : ''
                    }`}
                    onClick={() => handleGetSimilar(item[3]?.info?.big_name, index)}
                    disabled={loadingSimilar[index] || item[3]?.status !== 'found'}
                  >
                    {loadingSimilar[index] ? '⟳' : '→'}
                  </button>
                  <button
                    className={styles.removeButton}
                    onClick={() => removeMedicine(index)}
                  >
                    ✕
                  </button>
                </div>
                <div className={styles.medicineSubtitle}>
                  {item[3]?.status === 'found' ? item[3].info.big_name : 'Not found'}
                </div>
                {similarMedicines[index] && (
                  <div className={styles.similarMedicines}>
                    <h4>Similar Medicines:</h4>
                    <ul>
                      {similarMedicines[index]['similar_drugs'].map((med, i) => (
                        <li key={i}>{med['big_name']}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p>Upload a file to see results</p>
        )}
      </div>
    </div>
  );
}

export default PrescriptionUpload;