#%%
# Import the required libraries
import cv2
import numpy as np
import os
import pandas as pd 
from pathlib import Path
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model
from keras.applications.resnet50 import preprocess_input 
from keras.preprocessing import image
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

#%%


# Load the pre-trained ResNet model
model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Add a global average pooling layer
x = tf.keras.layers.GlobalAveragePooling2D()(model.output)

num_classes = 196

# Add a dense layer for classification (number of units = number of car brand classes)
output = tf.keras.layers.Dense(num_classes, activation='softmax')(x)

# Create the final model
model = tf.keras.models.Model(inputs=model.input, outputs=output)

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Function to load and preprocess image
def load_image(image_path):
    img = load_img(image_path, target_size=(224, 224))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = tf.keras.applications.resnet50.preprocess_input(img)  # Apply ResNet50-specific preprocessing
    return img

# Path to the folder containing car brand images
train_folder = r"C:\Users\scatt\Downloads\archive (1)\car_data\car_data\train"
test_folder = r"C:\Users\scatt\Downloads\archive (1)\car_data\car_data\test"

# List of car brand folders (Maserati, Ferrari, Volkswagen, etc.)
car_brands = os.listdir(train_folder)

# Create empty lists to store data and labels
train_data = []
train_labels = []



# Load images and labels for the training set
for brand_index, brand_name in enumerate(car_brands):
    brand_folder = Path(train_folder, brand_name)
    if os.path.isdir(brand_folder):  # Check if it's a valid directory
        for image_file in os.listdir(brand_folder):
            image_path = Path(brand_folder, image_file)
            if os.path.isfile(image_path):  # Check if it's a valid image file
                img = load_image(image_path)
                train_data.append(img)
                train_labels.append(brand_index)


# Convert lists to arrays for the training set
X_train = np.array(train_data)
y_train = np.array(train_labels)

# Convert the labels to one-hot encoded format
num_classes = len(car_brands)
y_train = to_categorical(y_train, num_classes=num_classes)

# Split the data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# Reshape the input data to remove the extra dimension
X_train = np.squeeze(X_train)
X_val = np.squeeze(X_val)

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

#%%
# Train the model
epochs = 2
batch_size = 32
model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_val, y_val))
#%%
# Save the model to a file
model.save(f'car_brand_model_2 - {epochs}.h5')

# Load the saved model
model = load_model(f'car_brand_model_2 - {epochs}.h5')
#%%
# ... (additional code if needed)

# Evaluate the model on the test set
test_data = []
test_labels = []

# Load images and labels for the test set
for brand_index, brand_name in enumerate(car_brands):
    brand_folder = Path(test_folder, brand_name)
    if os.path.isdir(brand_folder):  # Check if it's a valid directory
        for image_file in os.listdir(brand_folder):
            image_path = Path(brand_folder, image_file)
            if os.path.isfile(image_path):  # Check if it's a valid image file
                img = load_image(image_path)
                img = preprocess_input(img)    # Preprocess the input (if needed)
                test_data.append(img[0])
                test_labels.append(brand_index)
#%%
print(X_train.shape)
print(y_train.shape)
print(img)

import gc

gc.collect()
#%%
# Convert lists to arrays for the test set
X_test = np.array(test_data)
y_test = np.array(test_labels)


# Reshape the input data to remove the extra dimension
X_test = np.squeeze(X_test)
X_val = np.squeeze(X_val)
# Convert the labels to one-hot encoded format
y_test = to_categorical(y_test, num_classes=num_classes)

print(X_test.shape)
print(y_test.shape)
#%%
# Evaluate the model on the test set
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test loss: {loss}, Test accuracy: {accuracy}")
#%%

# Use the trained model to predict car brands on the test set
y_pred = model.predict(X_test[:1000])

# Decode the predicted labels
predicted_labels = np.argmax(y_pred, axis=1)
true_labels = np.argmax(y_train, axis=1)

# List of car brand names (assumed based on class indices)
car_brand_names = car_brands  # Replace with the actual names in your dataset

y_test_testing = y_test[0]
#%%
# Visualize the first 10 images along with their predicted and true labels
def visualize_predictions(images, predicted_labels, true_labels, class_names):
    plt.figure(figsize=(20, 10))
    plt.tight_layout()
    for i in range(len(images)):
        plt.subplot(6, 4, i + 1)
        plt.imshow(images[i])
        print(true_labels.shape)
        print(predicted_labels.shape)
        plt.title(f"Predicted: {class_names[predicted_labels[i]]}\nTrue: {class_names[true_labels[i]]}")
        plt.axis('off')
    plt.show()

# Visualize the first 10 images along with their predicted and true labels
#visualize_predictions(X_test[:10], predicted_labels[:10], y_test[:10], car_brand_names)
visualize_predictions(X_train[:20], predicted_labels[:20], true_labels[:20], car_brand_names)

# %%

# Use the trained model to predict car brands on the test set
y_pred = model.predict(X_test)

# Get the predicted labels from the one-hot encoded format
predicted_labels = np.argmax(y_pred, axis=1)
#%%
# Plot the confusion matrix
cm = confusion_matrix(np.argmax(y_test, axis=1), predicted_labels)

# Set the figure size and layout
plt.figure(figsize=(100, 50))
plt.tight_layout()

# Plot the confusion matrix with rotated x-axis labels and larger font size
disp.plot(cmap=plt.cm.Blues, values_format='.4g', xticks_rotation='vertical', ax=plt.gca())
plt.xticks(fontsize=8)  # Set a larger font size for x-axis labelsR
plt.yticks(fontsize=8)  # Set a larger font size for y-axis labels

# Set axis labels and title
plt.xlabel('Predicted Labels', fontsize=10)
plt.ylabel('True Labels', fontsize=10)
plt.title('Confusion Matrix', fontsize=12)



# %%
