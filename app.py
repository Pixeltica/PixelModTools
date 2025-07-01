import os
from flask import Flask, render_template, request, send_file, redirect
from werkzeug.utils import secure_filename
import zipfile
import shutil
import colormap_gen
import colorswap_util

app = Flask(__name__)

# Get the absolute path to the current file's directory
basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename, file_type):
    if file_type == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png'}
    elif file_type == 'csv':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}
    else:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    map_input_file_error = None
    recolor_base_file_error = None
    color_map_file_error = None
    csv_filename = None
    zip_filename = None

    if request.method == 'POST':
        if 'map_input_file' in request.files:  # Color map generation form
            map_input_file = request.files['map_input_file']
            if not allowed_file(map_input_file.filename, 'image'):
                map_input_file_error = "Invalid file type. Please upload a PNG image for color map."
                return render_template('index.html', map_input_file_error=map_input_file_error)

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(map_input_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            map_input_file.save(filepath)

            output_filename = 'color_map.csv'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

            try:
                colormap_gen.create_color_map(filepath, output_path)
                csv_filename = output_filename
                return render_template('index.html', csv_filename=csv_filename)
            except Exception as e:
                return f"An error occurred during color map generation: {e}"

        elif 'recolor_base_file' in request.files:  # Recolor generation form
            recolor_base_file = request.files['recolor_base_file']
            color_map_file = request.files.get('color_map_file')

            if not allowed_file(recolor_base_file.filename, 'image'):
                recolor_base_file_error = "Invalid file type. Please upload a PNG image for recoloring."
            if color_map_file and not allowed_file(color_map_file.filename, 'csv'):
                color_map_file_error = "Invalid file type. Please upload a CSV file for color map."
            if recolor_base_file_error or color_map_file_error:
                return render_template('index.html', 
                                       recolor_base_file_error=recolor_base_file_error, 
                                       color_map_file_error=color_map_file_error)

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            base_filename = secure_filename(recolor_base_file.filename)
            base_filepath = os.path.join(app.config['UPLOAD_FOLDER'], base_filename)
            recolor_base_file.save(base_filepath)

            if color_map_file:
                csv_filename = secure_filename(color_map_file.filename)
                csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
                color_map_file.save(csv_filepath)
            else:
                csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'color_map.csv')

            output_folder = os.path.join(basedir, 'recolored_images')  # Use basedir for output
            os.makedirs(output_folder, exist_ok=True)

            try:
                colorswap_util.swap_colors(csv_filepath, base_filepath, output_folder)

                zip_filename = 'recolored_images.zip'
                zip_path = os.path.join(output_folder, zip_filename)
                
                # Print the full path to the zip file
                print(f"Zip file path: {os.path.abspath(zip_path)}")

                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, _, files in os.walk(output_folder):
                        for file in files:
                            if file != zip_filename:
                                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_folder))

                return render_template('index.html', zip_filename=zip_filename)

            except Exception as e:
                return f"An error occurred during recoloring: {e}"

    print("Resetting form variables")  # Add this line
    csv_filename = None
    zip_filename = None
    print(f"csv_filename: {csv_filename}, zip_filename: {zip_filename}")
    return render_template('index.html',
                  map_input_file_error=map_input_file_error,
                  recolor_base_file_error=recolor_base_file_error,
                  color_map_file_error=color_map_file_error,
                  csv_filename=csv_filename,  # Pass the reset value
                  zip_filename=zip_filename)  # Pass the reset value

@app.route('/download/<filename>')
def download(filename):
    if filename == 'color_map.csv':
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    elif filename == 'recolored_images.zip':
        return send_file(os.path.join(basedir, 'recolored_images', filename), as_attachment=True)
    else:
        return "Invalid filename"
      
@app.route('/start_over')
def start_over():
    # Clear the uploads folder
    uploads_folder = app.config['UPLOAD_FOLDER']
    
    if os.path.exists(uploads_folder):
        for filename in os.listdir(uploads_folder):
            file_path = os.path.join(uploads_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

        

    # Clear the recolored_images folder
    recolored_folder = os.path.join(basedir, 'recolored_images')
    if os.path.exists(recolored_folder):
        for filename in os.listdir(recolored_folder):
            file_path = os.path.join(recolored_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=False)
    