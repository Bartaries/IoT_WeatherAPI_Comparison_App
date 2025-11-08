import * as THREE from 'three';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader.js';

let scene, camera, renderer;
let isDragging = false;
let previousMousePosition = { x: 0, y: 0 };
let esp32Group;

function init() {
    const container = document.getElementById('sensor-container');

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8f9fa);

    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 0, 50);
    camera.lookAt(0, 0, 0);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0x404040, 1.5);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 2);
    directionalLight.position.set(2, 5, 5);
    scene.add(directionalLight);
    const pointLight = new THREE.PointLight(0xffffff, 2);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    const textureLoader = new THREE.TextureLoader();
    const mainBoardTexture = textureLoader.load('/static/models/textures/IMG-1475.jpg');
    const detailTexture = textureLoader.load('/static/models/textures/IMG-1477.jpg');
    const aoMapTexture = textureLoader.load('/static/models/textures/internal_ground_ao_texture.jpeg');

    const fbxLoader = new FBXLoader();
    fbxLoader.load(
        '/static/models/DHT22.fbx',
        function(object) {
   
            object.traverse(function(child) {
                if (child instanceof THREE.Mesh && child.name.includes('DHT22')) {

                    child.material = new THREE.MeshStandardMaterial({ 
                        map: detailTexture,
                        aoMap: detailTexture
                    });
                }  
            });
            object.scale.set(13, 13, 13);
            object.position.set(0, 0, 0);

            esp32Group = new THREE.Group();
            esp32Group.add(object);
            scene.add(esp32Group);
        },
        function(xhr) { console.log((xhr.loaded / xhr.total * 100) + '% wczytano plik .fbx'); },
        function(error) { console.error('Błąd podczas ładowania .fbx', error); }
    );

    renderer.domElement.addEventListener('mousedown', onMouseDown);
    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('mouseup', onMouseUp);
    renderer.domElement.addEventListener('mouseleave', onMouseUp);
    renderer.domElement.addEventListener('dblclick', onDoubleClick);

    window.addEventListener('resize', onWindowResize);

    animate();
}


function getRelativeMousePos(e) {
    const rect = renderer.domElement.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
}

function onMouseDown(e) {
    isDragging = true;
    const pos = getRelativeMousePos(e);
    previousMousePosition.x = pos.x;
    previousMousePosition.y = pos.y;
}

function onMouseMove(e) {
    if (!isDragging || !esp32Group) return;
    const pos = getRelativeMousePos(e);
    const deltaX = pos.x - previousMousePosition.x;
    const deltaY = pos.y - previousMousePosition.y;
    const rotationSpeed = 0.007;

    const deltaRotY = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), deltaX * rotationSpeed);
    const deltaRotX = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), deltaY * rotationSpeed);

    esp32Group.quaternion.multiplyQuaternions(deltaRotY, esp32Group.quaternion);
    esp32Group.quaternion.multiplyQuaternions(deltaRotX, esp32Group.quaternion);

    previousMousePosition.x = pos.x;
    previousMousePosition.y = pos.y;
}

function onMouseUp() { 
    isDragging = false; 
}

function onDoubleClick() {
    if (esp32Group) {
        esp32Group.quaternion.set(0, 0, 0, 1);
    }
}

function onWindowResize() {
    const container = document.getElementById('sensor-container');
    if (container) {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }
}

function animate() {
    requestAnimationFrame(animate);

    if (esp32Group) {
        esp32Group.rotation.y += 0.015; 
    }

    renderer.render(scene, camera);
}

init();