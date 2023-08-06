/**
 * Copyright (c) 2009, 2010, Barthelemy Dagenais All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 * 
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 * 
 * - The name of the author may not be used to endorse or promote products
 * derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

package py4j;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Logger;

import py4j.model.Py4JMember;
import py4j.reflection.LRUCache;
import py4j.reflection.MethodInvoker;
import py4j.reflection.ReflectionEngine;

/**
 * 
 * <p>
 * Provides default implementation of a JavaGateway.
 * </p>
 * 
 * <p>
 * This class is <b>not</b> thread-safe. If the {@link py4j.GatewayServer
 * GatewayServer} allows multiple connections to the same gateway (acceptOnlyOne
 * == false), the javascript engine might be invoked by multiple threads with
 * unexpected consequences. The object and argument identifiers used by the
 * script engine are allocated in a thread-safe manner though.
 * </p>
 * 
 * <p>
 * If you plan to allow concurrent connections to a gateway, use
 * {@link py4j.DefaultSynchronizedGateway DefaultSynchronizedGateway} instead.
 * </p>
 * 
 * @see py4j.DefaultSynchronizedGateway DefaultSynchronizedGateway
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class Gateway {

	private final Map<String, Object> bindings = new ConcurrentHashMap<String, Object>();
	private final AtomicInteger objCounter = new AtomicInteger();
	private final AtomicInteger argCounter = new AtomicInteger();
	private final static String OBJECT_NAME_PREFIX = "o";
	private final Object entryPoint;
	private final ReflectionEngine rEngine = new ReflectionEngine();

	private final Logger logger = Logger.getLogger(Gateway.class.getName());

	private boolean isStarted = false;

	@SuppressWarnings("unused")
	private boolean cleanUpConnection = false;

	private static ThreadLocal<LRUCache<String,Py4JMember>> helpPages = new ThreadLocal<LRUCache<String,Py4JMember>>() {
		@Override
		protected LRUCache<String,Py4JMember> initialValue() {
			return new LRUCache<String,Py4JMember>();
		}
	};
	
	private static ThreadLocal<ConnectionProperty> connectionProperty = new ThreadLocal<ConnectionProperty>() {

		@Override
		protected ConnectionProperty initialValue() {
			return new ConnectionProperty();
		}

	};

	private static ThreadLocal<Set<String>> connectionObjects = new ThreadLocal<Set<String>>() {

		@Override
		protected Set<String> initialValue() {
			return new HashSet<String>();
		}

	};

	public Gateway(Object entryPoint) {
		this(entryPoint, false);
	}

	public Gateway(Object entryPoint, boolean cleanUpConnection) {
		this.entryPoint = entryPoint;
		this.cleanUpConnection = cleanUpConnection;
	}
	
	public ReturnObject attachObject(String objectId) {
		Object object = getObjectFromId(objectId);
		if (object == null) {
			throw new Py4JException("Cannot attach " + objectId
					+ ": it does not exist.");
		}
		return getReturnObject(object);
	}

	private void buildArgs(List<Argument> args, List<Object> parametersList) {
		for (Argument arg : args) {
			if (!arg.isReference()) {
				parametersList.add(arg.getValue());
			} else {
				parametersList.add(bindings.get(arg.getValue().toString()));
			}

		}
	}

	/**
	 * <p>
	 * Called when a connection is closed. Access ThreadLocal data to perform
	 * cleanup if necessary.
	 * </p>
	 * <p>
	 * Because there is one thread per connection, ThreadLocal data belong to a
	 * single connection.
	 * </p>
	 */
	public void closeConnection() {
		if (connectionProperty.get().isCleanConnection()) {
			logger.info("Cleaning Connection");
			for (String objectId : connectionObjects.get()) {
				this.bindings.remove(objectId);
			}
		}
	}

	public void deleteObject(String objectId) {
		bindings.remove(objectId);
		connectionObjects.get().remove(objectId);
	}

	protected AtomicInteger getArgCounter() {
		return argCounter;
	}

	protected Map<String, Object> getBindings() {
		return bindings;
	}

	public Object getEntryPoint() {
		return this.entryPoint;
	}

	public LRUCache<String,Py4JMember> getHelpPages() {
		return helpPages.get();
	}

	@SuppressWarnings("unchecked")
	public List<String> getMethodNames(Object obj) {
		Class clazz = obj.getClass();
		Method[] methods = clazz.getMethods();
		Set<String> methodNames = new HashSet<String>();
		for (Method method : methods) {
			methodNames.add(method.getName());
		}

		return new ArrayList<String>(methodNames);
	}

	public String getMethodNamesAsString(Object obj) {
		List<String> methodNames = getMethodNames(obj);
		StringBuilder buffer = new StringBuilder();
		for (String methodName : methodNames) {
			buffer.append(methodName);
			buffer.append(",");
		}
		return buffer.toString();
	}

	protected String getNextObjectId() {
		return OBJECT_NAME_PREFIX + objCounter.getAndIncrement();
	}

	protected AtomicInteger getObjCounter() {
		return objCounter;
	}

	/**
	 * 
	 * @param objectId
	 * @return The object associated with the id or null if the object id is
	 *         unknown.
	 */
	public Object getObject(String objectId) {
		if (objectId.equals(Protocol.CONNECTION_PROPERTY_OBJECT_ID)) {
			return connectionProperty.get();
		} else {
			return bindings.get(objectId);
		}
	}

	protected Object getObjectFromId(String targetObjectId) {
		if (targetObjectId.startsWith(Protocol.STATIC_PREFIX)) {
			return null;
		} else {
			return getObject(targetObjectId);
		}
	}

	public ReflectionEngine getReflectionEngine() {
		return rEngine;
	}

	@SuppressWarnings("unchecked")
	public ReturnObject getReturnObject(Object object) {
		ReturnObject returnObject;
		if (object != null) {
			if (isPrimitiveObject(object)) {
				returnObject = ReturnObject.getPrimitiveReturnObject(object);
			} else if (object == ReflectionEngine.RETURN_VOID) {
				returnObject = ReturnObject.getVoidReturnObject();
			} else if (isList(object)) {
				String objectId = putNewObject(object);
				returnObject = ReturnObject.getListReturnObject(objectId,
						((List) object).size());
			} else if (isMap(object)) {
				String objectId = putNewObject(object);
				returnObject = ReturnObject.getMapReturnObject(objectId,
						((Map) object).size());
			} else {
				String objectId = putNewObject(object);
				// TODO Handle lists, maps, etc.
				returnObject = ReturnObject.getReferenceReturnObject(objectId);
				trackConnectionObject(returnObject);
			}
		} else {
			returnObject = ReturnObject.getNullReturnObject();
		}
		return returnObject;
	}

	public ReturnObject invoke(String fqn, List<Argument> args) {
		if (args == null) {
			args = new ArrayList<Argument>();
		}
		ReturnObject returnObject = null;
		List<Object> parametersList = new ArrayList<Object>();
		try {
			buildArgs(args, parametersList);
			logger.info("Calling constructor: " + fqn);
			Object[] parameters = parametersList.toArray();

			MethodInvoker method = rEngine.getConstructor(fqn, parameters);
			Object object = rEngine.invoke(null, method, parameters);
			returnObject = getReturnObject(object);

		} catch (Exception e) {
			throw new Py4JException(e);
		}

		return returnObject;
	}

	public ReturnObject invoke(String methodName, String targetObjectId,
			List<Argument> args) {
		if (args == null) {
			args = new ArrayList<Argument>();
		}
		ReturnObject returnObject = null;
		List<Object> parametersList = new ArrayList<Object>();
		try {
			Object targetObject = getObjectFromId(targetObjectId);
			buildArgs(args, parametersList);
			logger.info("Calling: " + methodName);
			Object[] parameters = parametersList.toArray();

			MethodInvoker method = null;
			if (targetObject != null) {
				method = rEngine
						.getMethod(targetObject, methodName, parameters);
			} else {
				method = rEngine.getMethod(targetObjectId
						.substring(Protocol.STATIC_PREFIX.length()),
						methodName, parameters);
			}

			Object object = rEngine.invoke(targetObject, method, parameters);
			returnObject = getReturnObject(object);
		} catch (Exception e) {
			throw new Py4JException(e);
		}

		return returnObject;
	}

	@SuppressWarnings("unchecked")
	protected boolean isList(Object object) {
		return object instanceof List;
	}
	
	@SuppressWarnings("unchecked")
	protected boolean isMap(Object object) {
		return object instanceof Map;
	}

	protected boolean isPrimitiveObject(Object object) {
		return object instanceof Boolean || object instanceof String
				|| object instanceof Number || object instanceof Character;
	}

	public boolean isStarted() {
		return isStarted;
	}

	protected String putNewObject(Object object) {
		String id = getNextObjectId();
		bindings.put(id, object);
		return id;
	}

	public void setStarted(boolean isStarted) {
		this.isStarted = isStarted;
	}

	public void shutdown() {
		isStarted = false;
		bindings.clear();
	}

	public void startup() {
		isStarted = true;
		if (entryPoint != null) {
			bindings.put(Protocol.ENTRY_POINT_OBJECT_ID, entryPoint);
		}
	}

	private void trackConnectionObject(ReturnObject returnObject) {
		String name = returnObject.getName();
		if (name != null) {
			connectionObjects.get().add(returnObject.getName());
		}
	}
}
